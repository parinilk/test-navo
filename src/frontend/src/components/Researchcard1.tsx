


import { useNavigate } from "react-router-dom";

const Reportcard1 = () => {
  const navigate = useNavigate();


  return (
    <div className="flex-1 w-[1210px] h-[963px] bg-[#F7F8FC]">
      <div className="mt-2 ml-60 gap-[54px] w-[720px] h-[500px] bg-[#F7F8FC] rounded-lg">
        {/* Stepper */}
        <div className="flex items-center justify-center space-x-6">
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center">01</div>
            <p className="text-sm text-blue-600 font-medium mt-1">Context</p>
          </div>
          <div className="w-8 border-t-2 border-gray-300 mt-5" />
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 rounded-full bg-gray-200 text-black flex items-center justify-center">02</div>
            <p className="text-sm text-gray-500 mt-1">Research</p>
          </div>
        </div>

        {/* Heading */}
        <div className="flex justify-center mt-6">
          <p className="font-bold text-center">Tell us about your research</p>
        </div>

        {/* Role */}
        <div className="p-2">
          <div className="pl-20 font-semibold">Your Role</div>
          <div className="pl-20 text-medium">I am researching as</div>
          <div className="pl-20 mt-2">
            <input
              type="text"
              placeholder="Select your role"
              className="border border-gray-300 text-gray-500 rounded-lg p-2 w-[570px]  text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Objective */}
        <div className="p-2">
          <div className="pl-20 font-semibold">Objective</div>
          <div className="pl-20 test-base">What do you want to get out of this research?</div>
          <div className="pl-20 mt-1">
            <textarea
              placeholder="This research aims to..."
              className="border border-gray-300 text-gray-500 rounded-lg p-2 h-[55px] w-[570px] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Topic */}
        <div className="p-3">
          <div className="pl-20 font-semibold">Topic</div>
          <div className="pl-20 text-base">What is your research about?</div>
          <div className="pl-20 mt-1">
            <textarea
              placeholder="I'm researching...."
              className="border border-gray-300 text-gray-500 rounded-lg p-2 w-[570px] h-[55px] text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>


        <div className="flex justify-end pr-14 pt-4">
          <button
            onClick={() => navigate("/researchcard2")}
            className="bg-blue-500 text-white px-3 py-1 rounded"
          >
            Next
          </button>
        </div>

        <span className="pl-[90px]"> Or Select a Templete</span>

        {/* Grid of cards */}
        <div className="grid grid-cols-2 w-[660px] pl-[90px] gap-2 mt-2">
          {/* Card 1 */}
          <div className=" border border-gray-400 bg-white shadow-md rounded-lg p-4 flex flex-col items-center hover:shadow-lg transition">
            <h3 className="font-semibold text-gray-400">Product Positioning </h3>
          </div>

          {/* Card 2 */}
          <div className="border border-gray-400 bg-white shadow-md rounded-lg p-4 flex flex-col items-center hover:shadow-lg transition">
            <h3 className="font-semibold text-gray-400">Pricing Strategy</h3>
          </div>

          {/* Card 3 */}
          <div className="border border-gray-400 bg-white shadow-md rounded-lg p-4 flex flex-col items-center hover:shadow-lg transition">
            <h3 className="font-semibold text-gray-400">Regulatory-Safe Ingrediens</h3>

          </div>

          {/* Card 4 */}
          <div className="border border-gray-400 bg-white shadow-md rounded-lg p-4 flex flex-col items-center hover:shadow-lg transition">
            <h3 className="font-semibold text-gray-400">Line Extension </h3>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reportcard1;



