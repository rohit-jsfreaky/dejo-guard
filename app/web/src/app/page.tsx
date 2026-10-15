import { AgentsBand } from "@/components/AgentsBand";
import { ClassTable } from "@/components/ClassTable";
import { Faq } from "@/components/Faq";
import { Features } from "@/components/Features";
import { FinalCta } from "@/components/FinalCta";
import { Footer } from "@/components/Footer";
import { GetStarted } from "@/components/GetStarted";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";

export default function Home() {
  return (
    <>
      <Hero />
      <AgentsBand />
      <HowItWorks />
      <ClassTable />
      <Features />
      <GetStarted />
      <Faq />
      <FinalCta />
      <Footer />
    </>
  );
}
