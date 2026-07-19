import { useEffect, useMemo, useState, type FormEvent } from "react";
import { apiDelete, apiGet, apiPatch, apiPost } from "../api/client";
import type { LedgerTransaction, NamedItem } from "../api/types";
import { useAuth } from "../auth/context";

type TransactionForm = {
  tx_date: string;
  amount: string;
  tx_type: "EXPENSE" | "INCOME";
  description: string;
  category_id: string;
  payment_method_id: string;
};

const today = new Intl.DateTimeFormat("sv-SE").format(new Date());
const currency = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0,
});

const emptyForm: TransactionForm = {
  tx_date: today,
  amount: "",
  tx_type: "EXPENSE",
  description: "",
  category_id: "",
  payment_method_id: "",
};

export function TransactionsPage() {
  const { user, loading } = useAuth();
  const [transactions, setTransactions] = useState<LedgerTransaction[]>([]);
  const [categories, setCategories] = useState<NamedItem[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<NamedItem[]>([]);
  const [form, setForm] = useState<TransactionForm>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [typeFilter, setTypeFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [paymentMethodFilter, setPaymentMethodFilter] = useState("");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadTransactions() {
    const query = new URLSearchParams();
    if (typeFilter) query.set("tx_type", typeFilter);
    if (startDate) query.set("start_date", startDate);
    if (endDate) query.set("end_date", endDate);
    if (categoryFilter) query.set("category_id", categoryFilter);
    if (paymentMethodFilter) {
      query.set("payment_method_id", paymentMethodFilter);
    }
    if (search.trim()) query.set("search", search.trim());
    const suffix = query.size ? `?${query}` : "";
    setTransactions(
      await apiGet<LedgerTransaction[]>(`/api/transactions${suffix}`),
    );
  }

  useEffect(() => {
    if (!user) return;
    Promise.all([
      apiGet<NamedItem[]>("/api/categories"),
      apiGet<NamedItem[]>("/api/payment-methods"),
      apiGet<LedgerTransaction[]>("/api/transactions"),
    ])
      .then(([categoryData, paymentData, transactionData]) => {
        setCategories(categoryData);
        setPaymentMethods(paymentData);
        setTransactions(transactionData);
        setForm((current) => ({
          ...current,
          category_id: current.category_id || String(categoryData[0]?.id ?? ""),
          payment_method_id:
            current.payment_method_id || String(paymentData[0]?.id ?? ""),
        }));
      })
      .catch((requestError: Error) => setError(requestError.message));
  }, [user]);

  const totals = useMemo(
    () =>
      transactions.reduce(
        (sum, item) => {
          sum[item.tx_type] += Number(item.amount);
          return sum;
        },
        { INCOME: 0, EXPENSE: 0 },
      ),
    [transactions],
  );

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const body = {
        ...form,
        amount: form.amount,
        category_id: Number(form.category_id),
        payment_method_id: Number(form.payment_method_id),
      };
      if (editingId) {
        await apiPatch<LedgerTransaction>(
          `/api/transactions/${editingId}`,
          body,
        );
      } else {
        await apiPost<LedgerTransaction>("/api/transactions", body);
      }
      setEditingId(null);
      setForm((current) => ({
        ...emptyForm,
        category_id: current.category_id,
        payment_method_id: current.payment_method_id,
      }));
      await loadTransactions();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id: number) {
    if (!window.confirm("이 거래를 삭제할까요?")) return;
    await apiDelete(`/api/transactions/${id}`);
    await loadTransactions();
  }

  function edit(item: LedgerTransaction) {
    setEditingId(item.id);
    setForm({
      tx_date: item.tx_date,
      amount: item.amount,
      tx_type: item.tx_type,
      description: item.description,
      category_id: String(item.category_id),
      payment_method_id: String(item.payment_method_id),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm((current) => ({
      ...emptyForm,
      category_id: current.category_id,
      payment_method_id: current.payment_method_id,
    }));
  }

  if (loading) return <section className="card">불러오는 중입니다.</section>;
  if (!user)
    return <section className="card">거래를 보려면 먼저 로그인하세요.</section>;

  return (
    <section className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">수입과 지출</p>
          <h1>거래 내역</h1>
        </div>
        <div className="inline-totals">
          <span className="positive">+{currency.format(totals.INCOME)}</span>
          <span className="negative">-{currency.format(totals.EXPENSE)}</span>
        </div>
      </div>

      <form className="card transaction-form" onSubmit={submit}>
        <h2>{editingId ? "거래 수정" : "새 거래"}</h2>
        <div className="form-grid">
          <label>
            날짜
            <input
              required
              type="date"
              value={form.tx_date}
              onChange={(event) =>
                setForm({ ...form, tx_date: event.target.value })
              }
            />
          </label>
          <label>
            구분
            <select
              value={form.tx_type}
              onChange={(event) =>
                setForm({
                  ...form,
                  tx_type: event.target.value as TransactionForm["tx_type"],
                })
              }
            >
              <option value="EXPENSE">지출</option>
              <option value="INCOME">수입</option>
            </select>
          </label>
          <label>
            금액
            <input
              required
              min="1"
              step="0.01"
              type="number"
              value={form.amount}
              onChange={(event) =>
                setForm({ ...form, amount: event.target.value })
              }
              placeholder="0"
            />
          </label>
          <label>
            카테고리
            <select
              required
              value={form.category_id}
              onChange={(event) =>
                setForm({ ...form, category_id: event.target.value })
              }
            >
              {categories.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            결제수단
            <select
              required
              value={form.payment_method_id}
              onChange={(event) =>
                setForm({ ...form, payment_method_id: event.target.value })
              }
            >
              {paymentMethods.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          <label className="span-two">
            메모
            <input
              maxLength={500}
              value={form.description}
              onChange={(event) =>
                setForm({ ...form, description: event.target.value })
              }
              placeholder="어디에 사용했나요?"
            />
          </label>
        </div>
        {error && <p className="notice error">{error}</p>}
        <div className="filters">
          <button className="button" disabled={saving} type="submit">
            {saving ? "저장 중..." : editingId ? "수정 저장" : "거래 추가"}
          </button>
          {editingId && (
            <button
              className="button button-secondary"
              type="button"
              onClick={cancelEdit}
            >
              수정 취소
            </button>
          )}
        </div>
      </form>

      <div className="card">
        <div className="toolbar">
          <h2>기록</h2>
          <div className="filters">
            <input
              aria-label="시작일"
              type="date"
              value={startDate}
              onChange={(event) => setStartDate(event.target.value)}
            />
            <input
              aria-label="종료일"
              type="date"
              value={endDate}
              onChange={(event) => setEndDate(event.target.value)}
            />
            <select
              value={typeFilter}
              onChange={(event) => setTypeFilter(event.target.value)}
            >
              <option value="">전체 구분</option>
              <option value="INCOME">수입</option>
              <option value="EXPENSE">지출</option>
            </select>
            <select
              aria-label="카테고리 필터"
              value={categoryFilter}
              onChange={(event) => setCategoryFilter(event.target.value)}
            >
              <option value="">전체 카테고리</option>
              {categories.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <select
              aria-label="결제수단 필터"
              value={paymentMethodFilter}
              onChange={(event) => setPaymentMethodFilter(event.target.value)}
            >
              <option value="">전체 결제수단</option>
              {paymentMethods.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="메모·카테고리 검색"
            />
            <button
              className="button button-secondary"
              type="button"
              onClick={loadTransactions}
            >
              조회
            </button>
          </div>
        </div>
        {transactions.length === 0 ? (
          <p className="muted">아직 기록된 거래가 없습니다.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>구분</th>
                  <th>내용</th>
                  <th>수단</th>
                  <th className="number">금액</th>
                  <th aria-label="작업" />
                </tr>
              </thead>
              <tbody>
                {transactions.map((item) => (
                  <tr key={item.id}>
                    <td>{item.tx_date}</td>
                    <td>
                      <span
                        className={`type-pill ${item.tx_type.toLowerCase()}`}
                      >
                        {item.tx_type === "INCOME" ? "수입" : "지출"}
                      </span>
                    </td>
                    <td>
                      <strong>{item.category_name}</strong>
                      <small>{item.description || "메모 없음"}</small>
                    </td>
                    <td>{item.payment_method_name}</td>
                    <td
                      className={`number ${item.tx_type === "INCOME" ? "positive" : "negative"}`}
                    >
                      {item.tx_type === "INCOME" ? "+" : "-"}
                      {currency.format(Number(item.amount))}
                    </td>
                    <td>
                      <button
                        className="link-button"
                        type="button"
                        onClick={() => edit(item)}
                      >
                        수정
                      </button>{" "}
                      <button
                        className="link-button danger"
                        type="button"
                        onClick={() => remove(item.id)}
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
