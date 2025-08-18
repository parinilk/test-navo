
const Navbar = () => {
    return (
        <nav className="flex items-center justify-between px-[18px] py-[8px] w-full h-[54px]">
            <div>
                <span className="inline-block w-[56px] h-[28px] font-semibold text-[24px]">Navo</span>
            </div>
            <button className="flex items-center gap-2 bg-[#005CCE] text-white text-xs px-[16px] py-[8px] rounded-md">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none" className="text-white={value.toString()}">
                    <path d="M3.75 9H14.25M9 3.75V14.25" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            Start New Research
            </button>
        </nav>
    );
};

export default Navbar;
