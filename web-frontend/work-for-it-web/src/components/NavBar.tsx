import { NavLink } from "react-router-dom";


const TABS = [
    {label: "Product", path: "/product-section"},
    {label: "How it Works", path: "/how-it-works-section"},
    {label: "Privacy", path: "/privacy-section"}
]

const DARK="#090c10";

function NavLinks(){
    return(
        <div>
            {TABS.map((tab) => {
                return(
                    <NavLink key={tab.path} to={tab.path} end={tab.path === "/"}>
                        {tab.label}
                    </NavLink>
                )
            })}
        </div>
    )
}
export default function NavBar() {
    return(
    <div style={{display: "grid", maxWidth: "100%", gridTemplateColumns: "1fr auto 1fr", alignItems: "center", background: DARK, borderBottom: "1px solid rgba(255,255,255,0.15)",}}>
        <NavLinks />
    </div>
    )
}
