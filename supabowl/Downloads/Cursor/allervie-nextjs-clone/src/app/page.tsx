export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-6">Allervie Analytics Dashboard</h1>
      <p className="text-xl">Welcome to the Allervie Analytics Dashboard</p>
      <div className="mt-8 p-6 bg-blue-50 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Status</h2>
        <p className="text-green-600 font-medium">✅ Application Running Successfully</p>
      </div>
    </div>
  );
}
