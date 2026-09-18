import { NavLink } from "react-router-dom";


const TABS = [
    {label: "Product", path: "/"},
    {label: "How it Works", path: "/how-it-works-section"},
    {label: "Privacy", path: "/privacy-section"}
]

const DARK="#090c10";
const RED = "#e8161b"
const CONDENSED = "'Barlow Condensed', sans-serif";

function NavLinks(){
    return(
        <div style={{background: DARK, display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", alignItems: "stretch", width: "100%",
            borderBottom: "1px solid rgba(255,255,255,0.15)"
        }}>
            {TABS.map((tab) => {
                return(
                    <NavLink key={tab.path} to={tab.path} end={tab.path === "/"}
                    style={({ isActive }) => ({
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: "25px 15px",
                    minWidth: 0,
                    textDecoration: "none",
                    fontFamily: CONDENSED,
                    fontWeight: 700,
                    fontSize: 17,
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: isActive ? RED : "white",
                    borderBottom: isActive ? `2px solid ${RED}` : "2px solid transparent",
                    transition: "color 0.5s", userSelect: "none",
                    
                    })}
                    >
                        {tab.label}
                    </NavLink>
                )
            })}
        </div>
    )
}
export default function NavBar() {
    return(
    <div style={{maxWidth: "100%", background: DARK}}>
        <NavLinks />
    </div>
    )
}
