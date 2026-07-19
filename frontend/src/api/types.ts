export type CurrentUser = {
  id: number;
  email: string;
  role: "OWNER" | "USER";
  enabled: boolean;
  created_at: string;
};

export type NamedItem = {
  id: number;
  name: string;
  enabled: boolean;
};

export type LedgerTransaction = {
  id: number;
  tx_date: string;
  amount: string;
  tx_type: "INCOME" | "EXPENSE";
  description: string;
  category_id: number;
  category_name: string;
  payment_method_id: number;
  payment_method_name: string;
  created_at: string;
};

export type TransactionSummary = {
  income: string;
  expense: string;
  balance: string;
};

export type Account = CurrentUser;

export type Backup = {
  name: string;
  size: number;
  created_at: string;
};
