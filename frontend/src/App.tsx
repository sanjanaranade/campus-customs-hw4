import { FormEvent, useEffect, useState } from 'react'

type Page = 'home' | 'products' | 'about' | 'login' | 'account'
type InventoryRow = { size: string; quantity: number }
type Product = { product_id: string; name: string; type: string; price: number; description: string; image: string; inventory: InventoryRow[]; discount_percent?: number; sale_price?: number | null }
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function imageUrl(path: string): string {
  return path.startsWith('http') ? path : `${API_URL}${path}`
}

const catalogueProducts: Product[] = [
  { product_id: '2025-yale-vs-harvard-t-shirt', name: '2025 Yale Vs Harvard T Shirt', type: 'Short-sleeve T-shirt', price: 32, description: 'Heather gray short-sleeve T-shirt featuring a 2025 Harvard-Yale The Game graphic, with red Harvard and navy Yale football helmets facing each other and collegiate team marks.', image: '/media/products/2025-yale-vs-harvard-t-shirt.jpg', inventory: [{ size: 'XS', quantity: 25 }, { size: 'S', quantity: 25 }, { size: 'M', quantity: 20 }, { size: 'L', quantity: 2 }, { size: 'XL', quantity: 25 }, { size: 'XXL', quantity: 15 }] },
  { product_id: 'baseball-left-chest-crewneck', name: 'Baseball Left Chest Crewneck', type: 'Crewneck sweatshirt', price: 58, description: 'Navy long-sleeve crewneck sweatshirt with ribbed collar, cuffs, and waistband, featuring a white YALE BASEBALL wordmark on the left chest.', image: '/media/products/baseball-left-chest-crewneck.jpg', inventory: [{ size: 'XS', quantity: 0 }, { size: 'S', quantity: 15 }, { size: 'M', quantity: 5 }, { size: 'L', quantity: 25 }, { size: 'XL', quantity: 0 }, { size: 'XXL', quantity: 25 }] },
  { product_id: 'basic-hoodie-big-yale', name: 'Basic Hoodie Big Yale', type: 'Pullover hoodie', price: 68, description: 'Navy pullover hoodie with a front kangaroo pocket, drawstring hood, and large white YALE lettering across the chest.', image: '/media/products/basic-hoodie-big-yale.jpg', inventory: [{ size: 'XS', quantity: 15 }, { size: 'S', quantity: 5 }, { size: 'M', quantity: 5 }, { size: 'L', quantity: 8 }, { size: 'XL', quantity: 2 }, { size: 'XXL', quantity: 25 }] },
  { product_id: 'benjamin-franklin-1-4-zip', name: 'Benjamin Franklin 1/4 Zip', type: 'Quarter-zip pullover', price: 72, description: 'Heather gray long-sleeve quarter-zip pullover with a stand collar, ribbed cuffs and hem, and a small multicolor Benjamin Franklin College crest with college name on the left chest.', image: '/media/products/benjamin-franklin-1-4-zip.jpg', inventory: [{ size: 'XS', quantity: 2 }, { size: 'S', quantity: 2 }, { size: 'M', quantity: 25 }, { size: 'L', quantity: 20 }, { size: 'XL', quantity: 0 }, { size: 'XXL', quantity: 2 }] },
  { product_id: 'benjamin-franklin-fleece-jacket', name: 'Benjamin Franklin Fleece Jacket', type: 'Full-zip fleece jacket', price: 98, description: 'Light gray heathered fleece jacket with a full-length dark gray zipper, stand collar, zippered hand pockets, and a small multicolor Benjamin Franklin crest with text on the left chest.', image: '/media/products/benjamin-franklin-fleece-jacket.jpg', inventory: [{ size: 'XS', quantity: 0 }, { size: 'S', quantity: 12 }, { size: 'M', quantity: 5 }, { size: 'L', quantity: 2 }, { size: 'XL', quantity: 12 }, { size: 'XXL', quantity: 0 }] },
  { product_id: 'berkeley-1-4-zip', name: 'Berkeley 1/4 Zip', type: 'Quarter-zip pullover', price: 72, description: 'Heather gray long-sleeve quarter-zip pullover with a stand collar, ribbed cuffs and hem, and a red Berkeley shield crest with Berkeley text on the left chest.', image: '/media/products/berkeley-1-4-zip.jpg', inventory: [{ size: 'XS', quantity: 25 }, { size: 'S', quantity: 8 }, { size: 'M', quantity: 25 }, { size: 'L', quantity: 5 }, { size: 'XL', quantity: 8 }, { size: 'XXL', quantity: 12 }] },
]

const navItems: { label: string; page: Page }[] = [
  { label: 'Home', page: 'home' },
  { label: 'Products', page: 'products' },
  { label: 'About us', page: 'about' },
  { label: 'Log in', page: 'login' },
  { label: 'Create account', page: 'account' },
]

function productFromApi(product: Product & { image_url?: string; garment_type?: string }): Product {
  return { ...product, type: product.type ?? product.garment_type ?? 'Campus Customs piece', image: imageUrl(product.image_url ?? product.image) }
}

function App() {
  const [page, setPage] = useState<Page>('home')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [quickProduct, setQuickProduct] = useState<Product | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatResults, setChatResults] = useState<Product[]>([])
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; text: string; products?: Product[] }[]>([
    { role: 'assistant', text: 'Hi, Bulldog! I’m your Campus Customs guide. Ask me about Yale layers, sizes, or finding a gift—ruff!' },
  ])

  useEffect(() => {
    const onHashChange = () => {
      const next = window.location.hash.replace('#', '') as Page
      if (navItems.some((item) => item.page === next)) setPage(next)
    }
    onHashChange()
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    if (!chatOpen) return
    const token = localStorage.getItem('campus_customs_token')
    if (!token) return
    fetch(`${API_URL}/api/chat/history`, { headers: { Authorization: `Bearer ${token}` } }).then((response) => response.json()).then((data) => {
      if (data.messages?.length) setChatMessages(data.messages.map((item: { role: 'user' | 'assistant'; content: string; products?: Product[] }) => ({ role: item.role, text: item.content, products: (item.products ?? []).map(productFromApi) })))
    }).catch(() => undefined)
  }, [chatOpen])

  const navigate = (next: Page) => {
    window.location.hash = next
    setPage(next)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  const openProduct = (product: Product) => { setSelectedProduct(product); navigate('products') }
  const sendChat = async (event: FormEvent) => {
    event.preventDefault()
    const message = chatInput.trim()
    if (!message) return
    const history = chatMessages.map(({ role, text }) => ({ role, content: text }))
    setChatMessages((messages) => [...messages, { role: 'user', text: message }])
    setChatInput('')
    try { const token = localStorage.getItem('campus_customs_token'); const storedUser = localStorage.getItem('campus_customs_user'); const user = storedUser ? JSON.parse(storedUser) : null; const response = await fetch(`${API_URL}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, history, access_token: token, user_id: user?.id, page_context: `page=${page}${selectedProduct ? `; viewing product=${selectedProduct.name}; product_id=${selectedProduct.product_id}` : ''}` }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? 'The guide is unavailable right now.'); const products = (data.products ?? []).map(productFromApi); setChatResults(products); setChatMessages((messages) => [...messages, { role: 'assistant', text: data.reply, products }]) } catch (error) { setChatMessages((messages) => [...messages, { role: 'assistant', text: error instanceof Error && error.message.includes('unavailable') ? error.message : 'My paws cannot reach the shop guide right now. Please try again in a moment—ruff!' }]) }
  }

  return (
    <div className="site-shell">
      <CursorGlitter />
      <div className="announcement">Free campus delivery on orders over $75 <span>·</span> Made for Yale life</div>
      <header className="navbar">
        <div className="faint-paws" aria-hidden="true"><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span><span>🐾</span></div>
        <button className="wordmark" onClick={() => navigate('home')} aria-label="Campus Customs home">
          <span className="wordmark-mark">CC</span>
          <span><strong>CAMPUS</strong><em>CUSTOMS</em></span>
        </button>
        <div className="header-charms" aria-hidden="true"><span>✦</span><b>🐾</b><span>✦</span></div>
        <div className="header-mascot" aria-hidden="true"><div className="dog-body"><span className="dog-strap left" /><span className="dog-strap right" /><span className="dog-collar" /></div><div className="dog-backpack"><span className="backpack-pocket" /></div><div className="dog-face"><div className="dog-ear left" /><div className="dog-ear right" /><i className="dog-eye left" /><i className="dog-eye right" /><div className="dog-muzzle"><span /></div></div><div className="dog-bandana" /></div>
        <nav aria-label="Main navigation">
          {navItems.map((item) => (
            <button key={item.page} className={page === item.page ? 'nav-link active' : 'nav-link'} onClick={() => navigate(item.page)}>
              {item.label}
            </button>
          ))}
        </nav>
        <button className="bag-button" aria-label="Shopping bag">Bag <span>0</span></button>
      </header>
      <main>
        {page === 'home' && <Home navigate={navigate} onOpen={openProduct} />}
        {page === 'products' && (selectedProduct ? <ProductDetail product={selectedProduct} onBack={() => setSelectedProduct(null)} /> : <Products onOpen={openProduct} onQuickView={setQuickProduct} />)}
        {page === 'about' && <About navigate={navigate} />}
        {page === 'login' && <Auth mode="login" navigate={navigate} />}
        {page === 'account' && <Auth mode="account" navigate={navigate} />}
      </main>
      {chatResults.length > 0 && <section className="chat-results"><div className="chat-results-heading"><div><p className="eyebrow">FROM YOUR CHAT</p><h2>Guide <i>picks.</i></h2></div><button onClick={() => setChatResults([])} aria-label="Clear guide picks">Clear</button></div><div className="product-grid">{chatResults.map((product) => <ProductCard key={product.product_id} product={product} onOpen={() => openProduct(product)} />)}</div></section>}
      {quickProduct && <QuickView product={quickProduct} onClose={() => setQuickProduct(null)} onOpen={() => { setQuickProduct(null); openProduct(quickProduct) }} />}
      <aside className={chatOpen ? 'chat-panel open' : 'chat-panel'} aria-label="Campus Customs chat">
        {chatOpen && <div className="chat-window"><div className="chat-header"><div><span className="chat-status" />Campus Customs guide<p>Shopping assistant · live preview</p></div><button onClick={() => setChatOpen(false)} aria-label="Close chat">×</button></div><div className="chat-messages">{chatMessages.map((message, index) => <div key={`${message.role}-${index}`} className={`chat-message ${message.role}`}><span>{message.text}</span>{message.products && message.products.length > 0 && <div className="chat-products">{message.products.map((product) => <button key={product.product_id} onClick={() => openProduct(product)}>{product.name} · ${product.price}</button>)}</div>}</div>)}</div><form className="chat-form" onSubmit={sendChat}><input value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="Ask about the collection..." aria-label="Chat message" /><button type="submit" aria-label="Send message">↑</button></form></div>}
        <button className="chat-launcher" onClick={() => setChatOpen((open) => !open)} aria-expanded={chatOpen}><span className="chat-bubble-icon">✦</span>{chatOpen ? 'Close guide' : 'Ask Campus Customs'}<span className="chat-arrow">↗</span></button>
      </aside>
      <footer><span>© 2026 Campus Customs</span><span>Yale spirit, made personal.</span><span>Built for campus life.</span></footer>
    </div>
  )
}

function CursorGlitter() {
  const [sparkles, setSparkles] = useState<{ id: number; x: number; y: number }[]>([])

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    let nextId = 0
    const onPointerMove = (event: PointerEvent) => {
      if (event.pointerType !== 'mouse') return
      const sparkle = { id: nextId++, x: event.clientX, y: event.clientY }
      setSparkles((current) => [...current.slice(-9), sparkle])
      window.setTimeout(() => setSparkles((current) => current.filter((item) => item.id !== sparkle.id)), 560)
    }
    window.addEventListener('pointermove', onPointerMove)
    return () => window.removeEventListener('pointermove', onPointerMove)
  }, [])

  return <div className="cursor-glitter" aria-hidden="true">{sparkles.map((sparkle) => <span key={sparkle.id} className={`cursor-sparkle sparkle-${sparkle.id % 4}`} style={{ left: sparkle.x, top: sparkle.y }} />)}</div>
}

function Home({ navigate, onOpen }: { navigate: (page: Page) => void; onOpen: (product: Product) => void }) {
  return <>
    <section className="hero">
      <div className="hero-copy"><p className="eyebrow">THE YALE EDIT</p><h1>Wear your<br /><i>place</i>.</h1><p className="hero-text">From first day to final exam, find the layers that make campus feel like yours.</p><button className="button button-light" onClick={() => navigate('products')}>Explore the collection <span>↗</span></button></div>
      <div className="hero-stamp"><span>YALE</span><strong>EST.<br />1701</strong><span>NEW HAVEN</span></div>
    </section>
    <section className="intro-band"><p className="eyebrow">CAMPUS CUSTOMS</p><h2>Official spirit goods,<br /><i>with a point of view.</i></h2><p>Thoughtful staples and spirited layers for students, families, alumni, and every Bulldog at heart.</p></section>
    <section className="featured section"><div className="section-heading"><div><p className="eyebrow">SHOP THE FAVORITES</p><h2>Made for the <i>moment.</i></h2></div><button className="text-link" onClick={() => navigate('products')}>View all products ↗</button></div><div className="product-grid">{catalogueProducts.slice(0, 3).map((product) => <ProductCard key={product.product_id} product={product} onOpen={() => onOpen(product)} />)}</div></section>
    <section className="story-callout"><div><p className="eyebrow">THE CAMPUS CUSTOMS POINT OF VIEW</p><h2>More than a logo.<br /><i>It’s a feeling.</i></h2></div><button className="button button-outline" onClick={() => navigate('about')}>Our story <span>↗</span></button></section>
  </>
}

function Products({ onOpen, onQuickView }: { onOpen: (product: Product) => void; onQuickView: (product: Product) => void }) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [inStockOnly, setInStockOnly] = useState(false)
  const categories = [...new Set(catalogueProducts.map((product) => product.type))].sort()
  const filtered = catalogueProducts.filter((product) => (!search || `${product.name} ${product.description}`.toLowerCase().includes(search.toLowerCase())) && (category === 'all' || product.type === category) && (!inStockOnly || product.inventory.some((item) => item.quantity > 0)))
  const clearFilters = () => { setSearch(''); setCategory('all'); setInStockOnly(false) }
  return <section className="section products-page"><div className="page-heading"><p className="eyebrow">THE COLLECTION</p><h1>Find your <i>favorite.</i></h1><p>Yale layers, college pride, and everyday pieces for wherever campus takes you.</p></div><div className="filter-tools"><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search the collection" aria-label="Search products" /><select value={category} onChange={(event) => setCategory(event.target.value)} aria-label="Filter by category"><option value="all">All categories</option>{categories.map((item) => <option key={item} value={item}>{item}</option>)}</select><label className="stock-filter"><input type="checkbox" checked={inStockOnly} onChange={(event) => setInStockOnly(event.target.checked)} /> In stock only</label><button className="clear-filters" onClick={clearFilters}>Clear filters</button></div><div className="filter-row"><span>{filtered.length} of 102 catalogue pieces</span><span>Click a card for details · Quick view for a peek</span></div><div className="product-grid">{filtered.map((product) => <ProductCard key={product.product_id} product={product} onOpen={() => onOpen(product)} onQuickView={() => onQuickView(product)} />)}</div>{filtered.length === 0 && <div className="empty-state">No pieces match those filters. <button onClick={clearFilters}>Clear filters</button></div>}</section>
}

function ProductCard({ product, onOpen, onQuickView }: { product: Product; onOpen: () => void; onQuickView?: () => void }) {
  return <article className="product-card" onClick={onOpen} tabIndex={0} onKeyDown={(event) => { if (event.key === 'Enter') onOpen() }}><div className="product-image"><img src={imageUrl(product.image)} alt={product.name} /><button className="heart" aria-label={`Save ${product.name}`} onClick={(event) => event.stopPropagation()}>♡</button>{onQuickView && <button className="quick-view" onClick={(event) => { event.stopPropagation(); onQuickView() }}>Quick view</button>}</div><div className="product-info"><div><p>{product.type}</p><h3>{product.name}</h3><small>{product.description}</small></div><strong>{product.sale_price ? `$${product.sale_price}` : `$${product.price}`}</strong></div></article>
}

function QuickView({ product, onClose, onOpen }: { product: Product; onClose: () => void; onOpen: () => void }) {
  return <div className="modal-backdrop" role="presentation" onClick={onClose}><div className="quick-modal" role="dialog" aria-modal="true" aria-label={`Quick view ${product.name}`} onClick={(event) => event.stopPropagation()}><button className="modal-close" onClick={onClose} aria-label="Close quick view">×</button><img src={imageUrl(product.image)} alt={product.name} /><div><p className="eyebrow">{product.type}</p><h2>{product.name}</h2><strong className="detail-price">{product.sale_price ? `$${product.sale_price}` : `$${product.price}`}</strong><p>{product.description}</p><span className="modal-stock">{product.inventory.some((item) => item.quantity > 0) ? 'Available in selected sizes' : 'Currently unavailable'}</span><button className="button button-navy" onClick={onOpen}>View full details <span>↗</span></button></div></div></div>
}

function ProductDetail({ product, onBack }: { product: Product; onBack: () => void }) {
  const totalStock = product.inventory.reduce((total, row) => total + row.quantity, 0)
  return <section className="product-detail section"><button className="back-link" onClick={onBack}>← Back to products</button><div className="detail-layout"><div className="detail-image"><img src={imageUrl(product.image)} alt={product.name} /></div><div className="detail-copy"><p className="eyebrow">{product.type}</p><h1>{product.name}</h1><strong className="detail-price">${product.price}</strong><p className="detail-description">{product.description}</p><div className="stock-summary"><span className={totalStock > 0 ? 'in-stock' : 'out-stock'}>{totalStock > 0 ? 'In stock' : 'Currently unavailable'}</span><span>{totalStock} total units</span></div><h3>Choose a size</h3><div className="size-grid">{product.inventory.map((row) => <button key={row.size} disabled={row.quantity === 0}><span>{row.size}</span><small>{row.quantity > 0 ? `${row.quantity} available` : 'Sold out'}</small></button>)}</div><button className="button button-navy add-button" disabled={totalStock === 0}>Add to bag <span>↗</span></button></div></div></section>
}

function About({ navigate }: { navigate: (page: Page) => void }) {
  return <section className="about-page"><div className="about-hero"><p className="eyebrow">OUR STORY</p><h1>Built around<br /><i>belonging.</i></h1></div><div className="about-copy"><p className="eyebrow">WHY CAMPUS CUSTOMS</p><h2>Yale has a thousand ways to feel like home.</h2><p>Campus Customs is a place to find the piece that says where you’ve been, where you’re going, or who you’re cheering for. We bring together dependable everyday layers and unmistakably Yale details, with room for every kind of Bulldog to make them their own.</p><p>Our collection moves with campus life: from lecture halls to the stands, from family weekends to the quiet walk home. The best spirit wear doesn’t just mark a moment—it becomes part of the memory.</p><button className="button button-navy" onClick={() => navigate('products')}>Shop the collection <span>↗</span></button></div></section>
}

function Auth({ mode, navigate }: { mode: 'login' | 'account'; navigate: (page: Page) => void }) {
  const isLogin = mode === 'login'
  const [status, setStatus] = useState(''); const [busy, setBusy] = useState(false); const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
  const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setBusy(true); setStatus(''); const form = new FormData(event.currentTarget); const payload = isLogin ? { email: form.get('email'), password: form.get('password') } : { first_name: form.get('first_name'), last_name: form.get('last_name'), email: form.get('email'), password: form.get('password') }; if (!isLogin && form.get('password') !== form.get('confirm_password')) { setStatus('Passwords do not match.'); setBusy(false); return } try { const response = await fetch(`${apiUrl}/api/auth/${isLogin ? 'login' : 'register'}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail ?? 'Something went wrong.'); localStorage.setItem('campus_customs_token', data.access_token); localStorage.setItem('campus_customs_user', JSON.stringify(data.user)); setStatus(isLogin ? `Welcome back, ${data.user.first_name}.` : 'Account created! You can now log in.'); if (!isLogin) setTimeout(() => navigate('login'), 700) } catch (error) { setStatus(error instanceof Error ? error.message : 'Unable to connect to the Campus Customs API.') } finally { setBusy(false) } }
  return <section className="auth-page"><div className="auth-panel"><p className="eyebrow">CAMPUS CUSTOMS</p><h1>{isLogin ? 'Welcome back.' : 'Join the community.'}</h1><p>{isLogin ? 'Pick up where you left off.' : 'Save favorites, follow your orders, and make your campus style yours.'}</p><form onSubmit={submit}>{!isLogin && <div className="name-fields"><label>First name<input name="first_name" required autoComplete="given-name" /></label><label>Last name<input name="last_name" required autoComplete="family-name" /></label></div>}<label>Email address<input name="email" type="email" required autoComplete="email" placeholder="you@yale.edu" /></label><label>Password<input name="password" type="password" required minLength={8} autoComplete={isLogin ? 'current-password' : 'new-password'} placeholder="At least 8 characters" /></label>{!isLogin && <label>Confirm password<input name="confirm_password" type="password" required minLength={8} autoComplete="new-password" placeholder="Re-enter your password" /></label>}<button className="button button-navy" type="submit" disabled={busy}>{busy ? 'Please wait…' : isLogin ? 'Log in' : 'Create account'} <span>↗</span></button></form>{status && <p className="auth-status" role="status">{status}</p>}<button className="switch-auth" onClick={() => navigate(isLogin ? 'account' : 'login')}>{isLogin ? 'New here? Create an account' : 'Already have an account? Log in'}</button></div></section>
}

export default App
