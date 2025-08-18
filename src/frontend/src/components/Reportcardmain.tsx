
const Reportcardmain = () => {
  return (
    <div className="flex-1 p-[12px] w-[1210px] h-[550px] bg-[#F3F6FA]">
      {/* Header */}
      <h1 className="text-3xl font-semibold mb-2">Emerging Skincare trends 2025</h1>
      <div className="flex items-center text-sm text-gray-600 mb-4">
        <span>Date created: 08/10/2025</span>
        <span className="mx-3">|</span>
        <span>Created by: Jessie Lee</span>
        <span className="mx-3">|</span>
        <span>Role: Research Analyst</span>


        <button className="ml-auto flex items-center gap-2 bg-[#005CCE] text-white border border-blue-500 px-3 py-2 rounded text-sm hover:bg-blue-500 hover:text-white transition-colors duration-200">

          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12"
            />
          </svg>

          Export Report
        </button>




      </div>

      {/* Card content */}
      <div className="border rounded p-4 w-[1210px] h-[480px] bg-white overflow-y-auto">
        {/* Executive Summary */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Executive Summary</h2>
          <p className="text-sm text-gray-700 leading-relaxed">
            The global skincare market is entering a new phase in 2025, driven by shifting consumer values,
            scientific advancements, and digital-first retail experiences. Our competitive study identifies
            five emerging trends poised to shape brand strategy, product innovation, and customer engagement
            over the next 12–18 months.
          </p>
        </section>

        {/* Research Objective */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Research Objective</h2>
          <p className="text-sm font-semibold text-gray-700 mb-2">Key Research Questions (from pinned results):</p>
          <ul className="list-disc pl-6 text-sm text-gray-700">
            <li>Beauty and Wellness are the main key to success</li>
            <li>Beauty and Wellness are the main key to success</li>
            <li>Beauty and Wellness are the main key to success</li>
            <li>Beauty and Wellness are the main key to success</li>
            <li>Beauty and Wellness are the main key to success</li>
          </ul>
        </section>

        {/* Analysis & Findings */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Analysis & Findings</h2>
          <p className="text-sm font-semibold text-gray-700 mb-2">How Beauty and Wellness are the main key to success 💡</p>
          <ul className="list-disc pl-6 text-sm text-gray-700 space-y-1">
            <li>Success isn’t just about what you know — it’s about how you show up for the world.</li>
            <li>When you nurture your body, mind, and appearance, you radiate a presence that commands attention and inspires trust.</li>
            <li>Wellness fuels your drive. A healthy mind and body give you the stamina, clarity, and resilience to tackle challenges with grace.</li>
            <li>You think sharper, solve faster, and recover quicker.</li>
            <li>Beauty amplifies your impact. When you look your best, your projects and confidence speak before you say a word.</li>
            <li>People in wellness-driven connection make every opportunity more attainable.</li>
            <li>The combination fuels unstoppable momentum.</li>
          </ul>
        </section>

        {/* Conclusion */}
        <section>
          <h2 className="font-semibold text-lg mb-2">Conclusion & Recommendations</h2>
          <p className="text-sm font-semibold text-gray-700 mb-2">To stay competitive in 2025, companies should:</p>
          <ul className="list-disc pl-6 text-sm text-gray-700">
            <li>Invest in R&D for bioregenerative, neuromodulators, and hybrid formulas.</li>
            <li>Partner with AI and diagnostic tech providers.</li>
            <li>Build sustainability into the holistic lifestyle, not just packaging.</li>
            <li>Leverage influencer-led education to demystify emerging formats.</li>
          </ul>
        </section>
      </div>
    </div>
  );
};

export default Reportcardmain;
