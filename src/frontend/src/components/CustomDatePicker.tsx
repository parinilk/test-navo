import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useState } from "react";

function CustomDatePicker() {
  const [startDate, setStartDate] = useState<Date | null>(null);

  return (
    <div className="relative w-[230px] h-10">
    
      <div className="absolute inset-y-0 left-3 flex items-center z-20 pointer-events-none">
        
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
<path d="M6 1.5V4.5M12 1.5V4.5M2.25 7.5H15.75M6 10.5H6.0075M9 10.5H9.0075M12 10.5H12.0075M6 13.5H6.0075M9 13.5H9.0075M12 13.5H12.0075M3.75 3H14.25C15.0784 3 15.75 3.67157 15.75 4.5V15C15.75 15.8284 15.0784 16.5 14.25 16.5H3.75C2.92157 16.5 2.25 15.8284 2.25 15V4.5C2.25 3.67157 2.92157 3 3.75 3Z" stroke="black" stroke-width="1.125" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
      </div>

      {/* Datepicker input */}
      <DatePicker
        selected={startDate}
        onChange={(date) => setStartDate(date)}
        className="w-full h-9 pl-10 pr-6 border border-[#D0D5DD] rounded-lg text-sm text-[#344054] bg-white relative z-10"
        placeholderText="Creation date"
      />
    </div>
  );
}

export default CustomDatePicker;
