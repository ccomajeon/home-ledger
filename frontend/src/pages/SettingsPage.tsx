import { useEffect, useState, type FormEvent } from "react";
import { apiGet, apiPatch, apiPost } from "../api/client";
import type { NamedItem } from "../api/types";
import { useAuth } from "../auth/context";

type SettingGroupProps = {
  title: string;
  items: NamedItem[];
  endpoint: string;
  onChanged: () => Promise<void>;
};

function SettingGroup({
  title,
  items,
  endpoint,
  onChanged,
}: SettingGroupProps) {
  const [name, setName] = useState("");

  async function add(event: FormEvent) {
    event.preventDefault();
    await apiPost(endpoint, { name });
    setName("");
    await onChanged();
  }

  async function toggle(item: NamedItem) {
    await apiPatch(`${endpoint}/${item.id}`, { enabled: !item.enabled });
    await onChanged();
  }

  return (
    <article className="card">
      <h2>{title}</h2>
      <form className="inline-form" onSubmit={add}>
        <input
          required
          maxLength={100}
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder={`${title} 이름`}
        />
        <button className="button" type="submit">
          추가
        </button>
      </form>
      <ul className="setting-list">
        {items.map((item) => (
          <li key={item.id}>
            <span className={item.enabled ? "" : "disabled-text"}>
              {item.name}
            </span>
            <button
              className="button button-secondary button-small"
              type="button"
              onClick={() => toggle(item)}
            >
              {item.enabled ? "사용 중지" : "다시 사용"}
            </button>
          </li>
        ))}
      </ul>
    </article>
  );
}

export function SettingsPage() {
  const { user, loading } = useAuth();
  const [categories, setCategories] = useState<NamedItem[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<NamedItem[]>([]);

  async function loadCategories() {
    setCategories(
      await apiGet<NamedItem[]>("/api/categories?include_disabled=true"),
    );
  }

  async function loadPaymentMethods() {
    setPaymentMethods(
      await apiGet<NamedItem[]>("/api/payment-methods?include_disabled=true"),
    );
  }

  useEffect(() => {
    if (!user) return;
    Promise.all([
      apiGet<NamedItem[]>("/api/categories?include_disabled=true"),
      apiGet<NamedItem[]>("/api/payment-methods?include_disabled=true"),
    ]).then(([categoryData, paymentData]) => {
      setCategories(categoryData);
      setPaymentMethods(paymentData);
    });
  }, [user]);

  if (loading) return <section className="card">불러오는 중입니다.</section>;
  if (!user)
    return <section className="card">설정을 보려면 먼저 로그인하세요.</section>;

  return (
    <section className="stack">
      <div className="page-heading">
        <div>
          <p className="eyebrow">기록 기준 관리</p>
          <h1>가계부 설정</h1>
        </div>
      </div>
      <div className="two-column">
        <SettingGroup
          title="카테고리"
          items={categories}
          endpoint="/api/categories"
          onChanged={loadCategories}
        />
        <SettingGroup
          title="결제수단"
          items={paymentMethods}
          endpoint="/api/payment-methods"
          onChanged={loadPaymentMethods}
        />
      </div>
    </section>
  );
}
