import { RegisterForm } from "@/components/register-form";

export default function RegisterPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-indigo-200 to-sky-200 dark:from-indigo-900 dark:to-sky-900">
      <RegisterForm />
    </main>
  );
}

