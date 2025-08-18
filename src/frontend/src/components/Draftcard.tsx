

import { useEffect } from "react";
import { initFlowbite } from "flowbite";
import "flowbite/dist/flowbite.min.js";
import CustomDatePicker from "../components/CustomDatePicker";


function Draftcard() {
   useEffect(() => {
      initFlowbite();

   }, []);


   // function Draftcard() {
   return (
      <>

         <main className="flex-1 p-[12px] w-[1210px] h-[963px] bg-[#F7F8FC] overflow-y-auto">

            <div className="flex flex-col gap-2 mb-3">

               <h1 className="text-left font-semibold gap-[10px] w-[55px] h-[23px]">Drafts</h1>

               <div className=" flex gap-4">

                  {/* Card 1 */}

                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 w-1/3 flex flex-col gap-2">

                     <div className="flex justify-between">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <g clip-path="url(#clip0_178_1708)">
                              <path d="M10.05 1.49999H4.5C4.10218 1.49999 3.72064 1.65802 3.43934 1.93933C3.15804 2.22063 3 2.60216 3 2.99999V15C3 15.3978 3.15804 15.7793 3.43934 16.0606C3.72064 16.342 4.10218 16.5 4.5 16.5H13.5C13.8978 16.5 14.2794 16.342 14.5607 16.0606C14.842 15.7793 15 15.3978 15 15V9.44999M1.5 4.49999H4.5M1.5 7.49999H4.5M1.5 10.5H4.5M1.5 13.5H4.5M16.0335 4.21949C16.3323 3.92072 16.5001 3.51551 16.5001 3.09299C16.5001 2.67047 16.3323 2.26526 16.0335 1.96649C15.7347 1.66772 15.3295 1.49988 14.907 1.49988C14.4845 1.49988 14.0793 1.66772 13.7805 1.96649L10.023 5.72549C9.84469 5.90371 9.71416 6.12399 9.6435 6.36599L9.01575 8.51849C8.99693 8.58303 8.9958 8.65143 9.01248 8.71656C9.02917 8.78168 9.06305 8.84112 9.11058 8.88865C9.15812 8.93619 9.21756 8.97007 9.28268 8.98676C9.3478 9.00344 9.41621 9.00231 9.48075 8.98349L11.6332 8.35574C11.8752 8.28507 12.0955 8.15455 12.2737 7.97624L16.0335 4.21949Z" stroke="black" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" />
                           </g>
                           <defs>
                              <clipPath id="clip0_178_1708">
                                 <rect width="18" height="18" fill="white" />
                              </clipPath>
                           </defs>
                        </svg>

                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <path d="M9 9.75C9.41421 9.75 9.75 9.41421 9.75 9C9.75 8.58579 9.41421 8.25 9 8.25C8.58579 8.25 8.25 8.58579 8.25 9C8.25 9.41421 8.58579 9.75 9 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M14.25 9.75C14.6642 9.75 15 9.41421 15 9C15 8.58579 14.6642 8.25 14.25 8.25C13.8358 8.25 13.5 8.58579 13.5 9C13.5 9.41421 13.8358 9.75 14.25 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M3.75 9.75C4.16421 9.75 4.5 9.41421 4.5 9C4.5 8.58579 4.16421 8.25 3.75 8.25C3.33579 8.25 3 8.58579 3 9C3 9.41421 3.33579 9.75 3.75 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                     </div>
                     <span className="text-left text-sm">Draft</span>
                     <h5 className="text-[#101828] text-left font-semibold">Packaging trends Korea</h5>
                     <p className="text-xs text-[#667085] text-left">Last updated Today</p>
                     <span className="w-fit px-2 py-1 text-xs text-orange-400  bg-[#F1F1F1] rounded-full">In progress</span>
                  </div>

                  {/* Card 2 */}

                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 w-1/3 h-35 flex flex-col gap-2">


                     <div className="flex justify-between">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <g clip-path="url(#clip0_178_1708)">
                              <path d="M10.05 1.49999H4.5C4.10218 1.49999 3.72064 1.65802 3.43934 1.93933C3.15804 2.22063 3 2.60216 3 2.99999V15C3 15.3978 3.15804 15.7793 3.43934 16.0606C3.72064 16.342 4.10218 16.5 4.5 16.5H13.5C13.8978 16.5 14.2794 16.342 14.5607 16.0606C14.842 15.7793 15 15.3978 15 15V9.44999M1.5 4.49999H4.5M1.5 7.49999H4.5M1.5 10.5H4.5M1.5 13.5H4.5M16.0335 4.21949C16.3323 3.92072 16.5001 3.51551 16.5001 3.09299C16.5001 2.67047 16.3323 2.26526 16.0335 1.96649C15.7347 1.66772 15.3295 1.49988 14.907 1.49988C14.4845 1.49988 14.0793 1.66772 13.7805 1.96649L10.023 5.72549C9.84469 5.90371 9.71416 6.12399 9.6435 6.36599L9.01575 8.51849C8.99693 8.58303 8.9958 8.65143 9.01248 8.71656C9.02917 8.78168 9.06305 8.84112 9.11058 8.88865C9.15812 8.93619 9.21756 8.97007 9.28268 8.98676C9.3478 9.00344 9.41621 9.00231 9.48075 8.98349L11.6332 8.35574C11.8752 8.28507 12.0955 8.15455 12.2737 7.97624L16.0335 4.21949Z" stroke="black" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" />
                           </g>
                           <defs>
                              <clipPath id="clip0_178_1708">
                                 <rect width="18" height="18" fill="white" />
                              </clipPath>
                           </defs>
                        </svg>

                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <path d="M9 9.75C9.41421 9.75 9.75 9.41421 9.75 9C9.75 8.58579 9.41421 8.25 9 8.25C8.58579 8.25 8.25 8.58579 8.25 9C8.25 9.41421 8.58579 9.75 9 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M14.25 9.75C14.6642 9.75 15 9.41421 15 9C15 8.58579 14.6642 8.25 14.25 8.25C13.8358 8.25 13.5 8.58579 13.5 9C13.5 9.41421 13.8358 9.75 14.25 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M3.75 9.75C4.16421 9.75 4.5 9.41421 4.5 9C4.5 8.58579 4.16421 8.25 3.75 8.25C3.33579 8.25 3 8.58579 3 9C3 9.41421 3.33579 9.75 3.75 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                     </div><span className="text-left text-sm">Draft</span>
                     <h5 className="text-[#101828] text-left font-semibold">Cica masks popularity in the US</h5>
                     <p className="text-xs text-[#667085] text-left">Last updated Today</p>
                     <span className="w-fit px-2 py-1 text-xs text-orange-400  bg-[#F1F1F1] rounded-full">In progress</span>
                  </div>

                  {/* Card 3 */}

                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 w-1/3 flex flex-col gap-2">
                     <div className="flex justify-between">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <g clip-path="url(#clip0_178_1708)">
                              <path d="M10.05 1.49999H4.5C4.10218 1.49999 3.72064 1.65802 3.43934 1.93933C3.15804 2.22063 3 2.60216 3 2.99999V15C3 15.3978 3.15804 15.7793 3.43934 16.0606C3.72064 16.342 4.10218 16.5 4.5 16.5H13.5C13.8978 16.5 14.2794 16.342 14.5607 16.0606C14.842 15.7793 15 15.3978 15 15V9.44999M1.5 4.49999H4.5M1.5 7.49999H4.5M1.5 10.5H4.5M1.5 13.5H4.5M16.0335 4.21949C16.3323 3.92072 16.5001 3.51551 16.5001 3.09299C16.5001 2.67047 16.3323 2.26526 16.0335 1.96649C15.7347 1.66772 15.3295 1.49988 14.907 1.49988C14.4845 1.49988 14.0793 1.66772 13.7805 1.96649L10.023 5.72549C9.84469 5.90371 9.71416 6.12399 9.6435 6.36599L9.01575 8.51849C8.99693 8.58303 8.9958 8.65143 9.01248 8.71656C9.02917 8.78168 9.06305 8.84112 9.11058 8.88865C9.15812 8.93619 9.21756 8.97007 9.28268 8.98676C9.3478 9.00344 9.41621 9.00231 9.48075 8.98349L11.6332 8.35574C11.8752 8.28507 12.0955 8.15455 12.2737 7.97624L16.0335 4.21949Z" stroke="black" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" />
                           </g>
                           <defs>
                              <clipPath id="clip0_178_1708">
                                 <rect width="18" height="18" fill="white" />
                              </clipPath>
                           </defs>
                        </svg>

                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                           <path d="M9 9.75C9.41421 9.75 9.75 9.41421 9.75 9C9.75 8.58579 9.41421 8.25 9 8.25C8.58579 8.25 8.25 8.58579 8.25 9C8.25 9.41421 8.58579 9.75 9 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M14.25 9.75C14.6642 9.75 15 9.41421 15 9C15 8.58579 14.6642 8.25 14.25 8.25C13.8358 8.25 13.5 8.58579 13.5 9C13.5 9.41421 13.8358 9.75 14.25 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                           <path d="M3.75 9.75C4.16421 9.75 4.5 9.41421 4.5 9C4.5 8.58579 4.16421 8.25 3.75 8.25C3.33579 8.25 3 8.58579 3 9C3 9.41421 3.33579 9.75 3.75 9.75Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                     </div>

                     <span className="text-left text-sm">Draft</span>
                     <h5 className="text-[#101828]  font-semibold text-left">Latest patented products Japan</h5>
                     <p className="text-xs text-[#667085] text-left">Last updated Today</p>
                     <span className="w-fit px-2 py-1 text-xs text-orange-400 bg-[#F1F1F1] rounded-full">In progress</span>
                  </div>
               </div>
            </div>


            <div className="flex flex-col gap-1">

               <h1 className="text-left font-semibold gap-[10px] w-[55px] h-[23px]">Reports</h1>

               <div className="w-[1162px] h-[44px] ">

                  <div className="flex gap-4 mt-2 mb-4">

                     <div className="relative max-w-sm">
                        <div className="absolute inset-y-0  left-0 pl-3 flex items-center pointer-events-none">
                           <svg xmlns="http://www.w3.org/2000/svg"  width="18" height="18" viewBox="0 0 18 18" fill="none">
                              <path d="M15.75 15.75L12.495 12.495M14.25 8.25C14.25 11.5637 11.5637 14.25 8.25 14.25C4.93629 14.25 2.25 11.5637 2.25 8.25C2.25 4.93629 4.93629 2.25 8.25 2.25C11.5637 2.25 14.25 4.93629 14.25 8.25Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
                           </svg>
                        </div>
                        <input
                           type="text"
                           className="w-[200px] h-9 pl-10 border border-[#D0D5DD] rounded-lg bg-white text-sm text-[#344054]"
                           placeholder="Search"
                        />
                     </div>

                     <CustomDatePicker />


                     <button
                        id="dropdownHoverButton"
                        data-dropdown-toggle="dropdownHover"
                        data-dropdown-trigger="hover"
                        className="h-9 w-[200px] px-3 bg-white border border-[#D0D5DD] rounded-lg text-sm text-[#344054] inline-flex items-center hover:bg-blue-200"
                        type="button"
                     >
                        <span className="flex items-center gap-2">
                           <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="18"
                              height="18"
                              viewBox="0 0 18 18"
                              fill="none"
                           >
                              <path
                                 d="M2.25 12L5.25 15M5.25 15L8.25 12M5.25 15V3M15.75 6L12.75 3M12.75 3L9.75 6M12.75 3V15"
                                 stroke="black"
                                 strokeWidth="1.35"
                                 strokeLinecap="round"
                                 strokeLinejoin="round"
                              />
                           </svg>
                           Newest first
                        </span>
                     </button>




                     <div id="dropdownHover" className="z-10 hidden bg-white divide-y divide-gray-100 rounded-lg shadow-sm w-44 ">
                        <ul className="py-2 text-sm text-gray-700 dark:text-black-200" aria-labelledby="dropdownHoverButton">
                           <li>
                              <a href="#" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Item1</a>
                           </li>
                           <li>
                              <a href="#" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Item2</a>
                           </li>
                           <li>
                              <a href="#" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Item3</a>
                           </li>
                           <li>
                              <a href="#" className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Item4</a>
                           </li>
                        </ul>
                     </div>

                  </div>

               </div>

               <div className="flex flex-col gap-4">

                  {/* Card 1 */}

                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 flex flex-col gap-1">
                     <h2 className="text-[#101828] font-sm text-left">Market trends for collagen products in the US</h2>
                     <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#12B76A]"></span>
                        <p className="text-xs text-[#667085]">Complete · Created 2 days ago</p>
                        <p className="text-xs text-[#667085]">Complete · Created 2 days ago</p>
                     </div>
                  </div>

                  {/* Card 2 */}

                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 flex flex-col gap-1">
                     <h2 className="text-[#101828] text-left font-sm">Emerging skincare trends 2025</h2>
                     <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#12B76A]"></span>
                        <p className="text-sm text-[#667085]">Complete · Created 14 days ago</p>
                     </div>
                  </div>

                  {/* Card 3 */}


                  <div className="bg-white rounded-lg border border-[#EAECF0] p-4 flex flex-col gap-1">
                     <h2 className="text-[#101828] text-left font-sm">Glossier products pricing and market strategies</h2>
                     <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#12B76A]"></span>
                        <p className="text-sm text-[#667085]">Complete · Created 30 days ago</p>
                     </div>
                  </div>
               </div>
            </div>
         </main>
      </>
   )
}

export default Draftcard