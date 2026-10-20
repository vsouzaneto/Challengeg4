import { redirect } from "next/navigation";

// A página inicial é a carteira do vendedor.
export default function Home() {
  redirect("/carteira");
}
