import { Link, NavLink, Outlet } from 'react-router-dom'

export default function PublicLayout() {
  return (
    <div className="public-shell">
      <header className="public-nav">
        <Link className="brand public-brand" to="/">
          <span className="brand-mark">TP</span>
          TalentPath <small>PLACEMENT OPERATIONS</small>
        </Link>
        <nav>
          <NavLink to="/about">About</NavLink>
          <NavLink to="/services">Services</NavLink>
          <NavLink to="/contact">Contact</NavLink>
          <Link className="btn nav-cta" to="/login">Client Login</Link>
        </nav>
      </header>
      <Outlet />
      <footer className="public-footer">
        <div><Link className="brand" to="/"><span className="brand-mark">TP</span> TalentPath</Link><p>Human-led placement operations for faster Amazon opportunities.</p></div>
        <div className="footer-links"><Link to="/about">About</Link><Link to="/services">Services</Link><Link to="/contact">Contact</Link><Link to="/login">Client Login</Link></div>
        <div><strong>Support desk</strong><p>+92 333 2158308<br />hello@talentpath.pk</p></div>
        <small className="footer-bottom">© 2026 TalentPath. Placement, with precision.</small>
      </footer>
    </div>
  )
}