<?php
if ( ! defined( 'ABSPATH' ) ) exit;

$user_id        = get_current_user_id();
$user           = wp_get_current_user();
$first_name     = $user->first_name ? explode(' ', $user->first_name)[0] : '';
$last_name      = $user->last_name  ? explode(' ', $user->last_name)[0]  : '';
$nombre         = trim($first_name . ' ' . $last_name) ?: $user->display_name;
$image_url      = get_user_meta( $user_id, 'custom_profile_picture', true );
$logout_url     = wc_get_account_endpoint_url('customer-logout');

$is_orders      = is_wc_endpoint_url('orders') || is_wc_endpoint_url('view-order');
$is_address     = is_wc_endpoint_url('edit-address');
$is_account     = is_wc_endpoint_url('edit-account');
$is_default     = ! $is_orders && ! $is_address && ! $is_account; // landing /mi-cuenta/ => Beneficios

do_action( 'woocommerce_before_account_navigation' );
?>

<nav class="kd-sidebar woocommerce-MyAccount-navigation" aria-label="Navegación de cuenta">

	<!-- WooCommerce ul oculto - necesario para que WC detecte el endpoint activo -->
	<ul style="display:none; visibility:hidden; pointer-events:none;">
		<?php foreach ( wc_get_account_menu_items() as $endpoint => $label ) : ?>
			<li class="<?php echo wc_get_account_menu_item_classes( $endpoint ); ?>">
				<a href="<?php echo esc_url( wc_get_account_endpoint_url( $endpoint ) ); ?>"><?php echo esc_html( $label ); ?></a>
			</li>
		<?php endforeach; ?>
	</ul>

	<!-- CAJA 1: Perfil -->
	<div class="kd-profile-card">
		<img class="kd-profile-bg" src="https://www.tiendakrear3d.com/wp-content/uploads/2026/05/wp.webp" alt="">

		<div class="kd-avatar-wrap">
			<?php if ( $image_url ) : ?>
				<img src="<?php echo esc_url( $image_url ); ?>" alt="Perfil" class="kd-avatar-img">
			<?php else : ?>
				<img src="/wp-content/uploads/2025/07/cuenta.png" alt="Perfil" class="kd-avatar-img kd-avatar-default">
			<?php endif; ?>
			<div class="kd-avatar-dot"></div>
		</div>
		<p class="kd-name"><?php echo esc_html( $nombre ); ?></p>
		<p class="kd-username"><?php echo esc_html( $user->user_email ); ?></p>
	</div>

	<!-- CAJA 2: Menu -->
	<div class="kd-nav-card">

		<!-- Beneficios (seccion local: servicios) -->
		<a href="/mi-cuenta/" class="kd-nav-item kd-item-servicios <?php echo $is_default ? 'kd-active' : ''; ?>" data-nav data-kind="section" data-section="servicios">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
			</svg>
			<span>Beneficios</span>
		</a>

		<!-- Perfil -->
		<a href="/mi-cuenta/edit-account/" class="kd-nav-item kd-item-perfil <?php echo $is_account ? 'kd-active' : ''; ?>" data-nav data-kind="wc" data-endpoint="edit-account">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
			</svg>
			<span>Perfil</span>
		</a>

		<!-- Pedidos -->
		<a href="/mi-cuenta/?section=pedidos" class="kd-nav-item kd-item-pedidos <?php echo $is_orders ? 'kd-active' : ''; ?>" data-nav data-kind="section" data-section="pedidos" data-url="/mi-cuenta/?section=pedidos">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>
			</svg>
			<span>Pedidos</span>
		</a>

		<!-- Direcciones -->
		<a href="/mi-cuenta/edit-address/" class="kd-nav-item kd-item-direcciones <?php echo $is_address ? 'kd-active' : ''; ?>" data-nav data-kind="wc" data-endpoint="edit-address">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
			</svg>
			<span>Direcciones</span>
		</a>

		<!-- Programas (oculto temporalmente) -->

		<!-- Salir -->
		<a class="kd-nav-item kd-item-salir" href="<?php echo esc_url( $logout_url ); ?>">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
			</svg>
			<span>Cerrar sesión</span>
		</a>

	</div>
</nav>

<script>
document.addEventListener("DOMContentLoaded", function () {
	const dash    = document.getElementById("kd-dashboard");
	if (!dash) return;
	const content = dash.querySelector(".woocommerce-MyAccount-content");
	const wcPane  = document.getElementById("kd-wc-content");
	if (!content || !wcPane) return;

	const DEFAULT_SECTION = "servicios"; // "Beneficios" del menu

	const sections = {
		beneficios: document.getElementById("section-beneficios"),
		prime:      document.getElementById("section-prime"),
		afiliados:  document.getElementById("section-afiliados"),
		servicios:  document.getElementById("section-servicios"),
		guias:      document.getElementById("section-guias"),
		trueke:     document.getElementById("section-trueke"),
		pedidos:    document.getElementById("section-pedidos"),
	};

	// endpoint WC -> selector del item de menu a marcar activo
	const WC_KEYS = {
		"edit-account": ".kd-item-perfil",
		"orders":       ".kd-item-pedidos",
		"view-order":   ".kd-item-pedidos",
		"edit-address": ".kd-item-direcciones",
	};

	// Loader
	const loader = document.createElement("div");
	loader.className = "kd-loading";
	loader.innerHTML = '<span class="kd-spinner"></span>';

	// scripts ya ejecutados (evita redeclarar const al re-inyectar)
	const ranScripts = new Set();

	function clearActive() {
		dash.querySelectorAll(".kd-nav-item.kd-active").forEach(el => el.classList.remove("kd-active"));
	}
	function setActive(selector) {
		clearActive();
		if (selector) dash.querySelector(selector)?.classList.add("kd-active");
	}
	function hideSections() {
		Object.values(sections).forEach(s => s && (s.style.display = "none"));
	}

	function showProgram(name) {
		dash.querySelectorAll(".kd-prog-btn").forEach(b => b.classList.remove("active"));
		dash.querySelector(".kd-prog-btn." + name)?.classList.add("active");
		hideSections();
		if (sections[name]) sections[name].style.display = "flex";
	}

	function showSection(key) {
		hideSections();
		wcPane.style.display = "none";
		dash.classList.toggle("programas-activa", key === "programas");

		if (key === "programas") {
			dash.querySelector(".kd-programas-sub")?.classList.remove("kd-sub-hidden");
			setActive(".kd-item-programas");
			showProgram("beneficios");
		} else {
			if (!sections[key]) key = DEFAULT_SECTION;
			sections[key].style.display = "flex";
			setActive(".kd-item-" + key);
		}
	}

	function showWcPane(menuSelector) {
		hideSections();
		dash.classList.remove("programas-activa");
		wcPane.style.display = "";
		setActive(menuSelector);
	}

	function extractContent(html) {
		const doc  = new DOMParser().parseFromString(html, "text/html");
		const node = doc.querySelector("#kd-wc-content");
		if (!node) return { html: null, notices: "" };
		// Evita duplicar avisos: si ya vienen dentro del contenido, no los repetimos.
		let notices = "";
		const hasInside = node.querySelector(".woocommerce-message, .woocommerce-error, .woocommerce-info");
		if (!hasInside) {
			const outside = [...doc.querySelectorAll(".woocommerce-message, .woocommerce-error, .woocommerce-info")];
			if (outside.length) {
				notices = '<div class="woocommerce-notices-wrapper">' + outside.map(n => n.outerHTML).join("") + '</div>';
			}
		}
		return { html: node.innerHTML, notices };
	}

	function runScripts(container) {
		container.querySelectorAll("script").forEach(old => {
			const key = old.src || old.textContent;
			if (ranScripts.has(key)) { old.remove(); return; }
			ranScripts.add(key);
			const s = document.createElement("script");
			[...old.attributes].forEach(a => s.setAttribute(a.name, a.value));
			s.textContent = old.textContent;
			old.replaceWith(s);
		});
	}

	function inject(html, notices) {
		wcPane.innerHTML = (notices || "") + html;
		runScripts(wcPane);
		try { content.scrollIntoView({ block: "nearest", behavior: "smooth" }); } catch (e) {}
	}

	function addOrdersBackLink() {
		if (wcPane.querySelector(".kd-back-orders")) return;
		const back = document.createElement("a");
		back.href = "/mi-cuenta/?section=pedidos";
		back.className = "kd-back-orders";
		back.textContent = "← Mis pedidos";
		back.style.cssText = "display:inline-flex;align-items:center;gap:.35rem;margin:0 0 1rem;color:var(--primary,#e05a00);font-weight:600;text-decoration:none;cursor:pointer;";
		back.addEventListener("click", (e) => { e.preventDefault(); navigate("/mi-cuenta/?section=pedidos"); });
		wcPane.insertBefore(back, wcPane.firstChild);
	}

	async function loadWc(url, opts) {
		const push = !opts || opts.push !== false;
		wcPane.appendChild(loader);
		try {
			const res  = await fetch(url, { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } });
			const text = await res.text();
			const data = extractContent(text);
			if (data.html === null) { window.location.href = url; return; }
			inject(data.html, data.notices);
			if (detectEndpoint(new URL(url, location.origin).pathname) === "view-order") addOrdersBackLink();
			if (push) history.pushState({ kd: true }, "", res.url || url);
		} catch (e) {
			window.location.href = url; // fallback duro
		}
	}

	function detectEndpoint(pathname) {
		const path = pathname.replace(/\/+$/, "");
		const m = path.match(/\/(edit-account|orders|view-order|edit-address)(?:\/|$)/);
		return m ? m[1] : null;
	}

	function route(fetchWc) {
		const ep = detectEndpoint(location.pathname);
		if (ep && WC_KEYS[ep]) {
			showWcPane(WC_KEYS[ep]);
			if (ep === "view-order") addOrdersBackLink();
			if (fetchWc) loadWc(location.href, { push: false });
		} else {
			const section = new URLSearchParams(location.search).get("section") || DEFAULT_SECTION;
			showSection(section);
		}
	}

	function navigate(url) {
		let target;
		try { target = new URL(url, location.origin); } catch (e) { return; }
		const ep = detectEndpoint(target.pathname);
		if (ep && WC_KEYS[ep]) {
			showWcPane(WC_KEYS[ep]);
			loadWc(target.href, { push: true });
		} else {
			const section = target.searchParams.get("section") || DEFAULT_SECTION;
			showSection(section);
			history.pushState({ kd: true }, "", target.pathname + target.search);
		}
	}

	// Items del menu
	dash.querySelectorAll("[data-nav]").forEach(item => {
		item.addEventListener("click", (e) => {
			e.preventDefault();
			navigate(item.getAttribute("href") || item.dataset.url || "/mi-cuenta/");
		});
	});

	// Sub-botones de Programas
	dash.querySelectorAll(".kd-prog-btn").forEach(btn => {
		btn.addEventListener("click", () => {
			const name = ["beneficios", "prime", "afiliados", "trueke", "servicios"].find(c => btn.classList.contains(c));
			if (name) showProgram(name);
		});
	});

	// Links internos del contenido y de la lista de pedidos (ver pedido, editar direccion, paginacion)
	content.addEventListener("click", (e) => {
		const a = e.target.closest("a");
		if (!a || !content.contains(a)) return;
		const href = a.getAttribute("href") || "";
		if (!href || href.charAt(0) === "#") return;
		let u; try { u = new URL(href, location.origin); } catch (e2) { return; }
		if (u.origin === location.origin && /\/mi-cuenta\/(edit-account|orders|view-order|edit-address)/.test(u.pathname)) {
			e.preventDefault();
			navigate(u.href);
		}
	});

	// Submit de formularios WC (perfil, direcciones) sin recargar
	let lastSubmitter = null;
	wcPane.addEventListener("click", (e) => {
		const b = e.target.closest("button[type=submit], input[type=submit], button:not([type])");
		if (b && wcPane.contains(b)) lastSubmitter = b;
	});
	wcPane.addEventListener("submit", async (e) => {
		const form = e.target.closest("form");
		if (!form || !wcPane.contains(form)) return;
		e.preventDefault();
		const fd = new FormData(form);
		if (lastSubmitter && lastSubmitter.name) fd.append(lastSubmitter.name, lastSubmitter.value || "");
		// Guardado independiente: al guardar la info no mandamos los campos de contrasena
		// (evita el error de "rellena todos los campos de contrasena" por autocompletado).
		if (lastSubmitter && lastSubmitter.value === "save_info") {
			fd.delete("password_current");
			fd.delete("password_1");
			fd.delete("password_2");
		}
		const action = (form.getAttribute("action") || "").trim();
		const url = action || location.href;
		wcPane.appendChild(loader);
		try {
			const res  = await fetch(url, { method: "POST", body: fd, credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } });
			const text = await res.text();
			const data = extractContent(text);
			if (data.html === null) { form.submit(); return; }
			inject(data.html, data.notices);
		} catch (err) {
			form.submit();
		} finally {
			lastSubmitter = null;
		}
	});

	// Atras / Adelante
	window.addEventListener("popstate", () => route(true));

	// Init: en la carga inicial el contenido WC ya viene renderizado por PHP
	route(false);
});
</script>

<?php do_action( 'woocommerce_after_account_navigation' ); ?>
