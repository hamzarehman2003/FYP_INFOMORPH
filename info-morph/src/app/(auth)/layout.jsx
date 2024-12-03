import Layout from "@/components/Auth/layout";

export default function AuthLayout({ children }) {
  return (
    <main className="flex min-h-screen">
      <Layout />
      {children}
    </main>
  );
}
