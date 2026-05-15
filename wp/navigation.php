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
$is_account     = is_wc_endpoint_url('edit-account') || ( !$is_orders && !$is_address );

do_action( 'woocommerce_before_account_navigation' );
?>

<nav class="kd-sidebar woocommerce-MyAccount-navigation" aria-label="Navegación de cuenta">

	<!-- WooCommerce ul oculto — necesario para que WC detecte el endpoint activo -->
	<ul style="display:none; visibility:hidden; pointer-events:none;">
		<?php foreach ( wc_get_account_menu_items() as $endpoint => $label ) : ?>
			<li class="<?php echo wc_get_account_menu_item_classes( $endpoint ); ?>">
				<a href="<?php echo esc_url( wc_get_account_endpoint_url( $endpoint ) ); ?>"><?php echo esc_html( $label ); ?></a>
			</li>
		<?php endforeach; ?>
		<li class="custom-menu-item programas" data-section="programas">
			<a href="<?php echo esc_url( home_url( '/mi-cuenta/?section=programas' ) ); ?>" class="nav-link">Programas</a>
		</li>
	</ul>

	<!-- CAJA 1: Perfil -->
	<div class="kd-profile-card">
		<div class="kd-avatar-wrap">
			<?php if ( $image_url ) : ?>
				<img src="<?php echo esc_url( $image_url ); ?>" alt="Perfil" class="kd-avatar-img">
			<?php else : ?>
				<img src="/wp-content/uploads/2025/07/cuenta.png" alt="Perfil" class="kd-avatar-img kd-avatar-default">
			<?php endif; ?>
		</div>
		<p class="kd-name"><?php echo esc_html( $nombre ); ?></p>
		<p class="kd-username"><?php echo esc_html( $user->display_name ); ?></p>
	</div>

	<!-- CAJA 2: Menú -->
	<div class="kd-nav-card">

		<!-- Perfil -->
		<div class="kd-nav-group <?php echo $is_account ? 'kd-group-open' : ''; ?>">
			<a href="/mi-cuenta/edit-account/" class="kd-nav-item kd-item-perfil <?php echo $is_account ? 'kd-active' : ''; ?>">
				<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
				</svg>
				<span>Perfil</span>
			</a>
			<div class="kd-nav-sub <?php echo $is_account ? '' : 'kd-sub-hidden'; ?>">
				<button class="kd-sub-btn kd-btn-info active">Información Personal</button>
				<button class="kd-sub-btn kd-btn-pass">Contraseña</button>
			</div>
		</div>

		<!-- Pedidos -->
		<a class="kd-nav-item <?php echo $is_orders ? 'kd-active' : ''; ?>" href="/mi-cuenta/orders/">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/>
			</svg>
			<span>Pedidos</span>
		</a>

		<?php if ( $is_orders ) :
			$customer_orders = wc_get_orders(['customer_id' => $user_id, 'limit' => -1]);
			if ( $customer_orders ) :
				$current_order_id = get_query_var('view-order');
		?>
			<div class="kd-orders-sub">
				<?php foreach ( $customer_orders as $order ) :
					$active_cl = ( $order->get_id() == $current_order_id ) ? 'kd-sub-active' : '';
				?>
					<a href="<?php echo esc_url( $order->get_view_order_url() ); ?>" class="kd-order-link <?php echo $active_cl; ?>">
						Pedido <span>#<?php echo esc_html( $order->get_order_number() ); ?></span>
					</a>
				<?php endforeach; ?>
			</div>
		<?php endif; endif; ?>

		<!-- Direcciones -->
		<a class="kd-nav-item <?php echo $is_address ? 'kd-active' : ''; ?>" href="/mi-cuenta/edit-address/">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
			</svg>
			<span>Direcciones</span>
		</a>

		<!-- Programas -->
		<div class="kd-nav-group">
			<div class="kd-nav-item kd-item-programas custom-menu-item programas" data-section="programas">
				<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
				</svg>
				<span>Programas</span>
			</div>
			<div class="kd-nav-sub kd-programas-sub kd-sub-hidden">
				<button class="kd-sub-btn kd-prog-btn beneficios active">+Beneficios</button>
				<button class="kd-sub-btn kd-prog-btn prime">Prime</button>
				<button class="kd-sub-btn kd-prog-btn afiliados">Afiliados</button>
				<button class="kd-sub-btn kd-prog-btn trueke">Trueke</button>
			</div>
		</div>

		<!-- Servicios -->
		<div class="kd-nav-item kd-item-servicios">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
			</svg>
			<span>Servicios</span>
		</div>

		<!-- Salir -->
		<a class="kd-nav-item kd-item-salir" href="<?php echo esc_url( $logout_url ); ?>">
			<svg class="kd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
			</svg>
			<span>Salir</span>
		</a>

	</div>
</nav>

<script>
document.addEventListener("DOMContentLoaded", function () {

	// ── Info / Contraseña toggle ──────────────────────────────────────────
	const btnInfo = document.querySelector(".kd-btn-info");
	const btnPass = document.querySelector(".kd-btn-pass");
	const form    = document.querySelector(".woocommerce-EditAccountForm");

	if (btnInfo && btnPass && form) {
		btnInfo.addEventListener("click", function () {
			btnInfo.classList.add("active");
			btnPass.classList.remove("active");
			form.classList.remove("page-pass");
		});
		btnPass.addEventListener("click", function () {
			btnPass.classList.add("active");
			btnInfo.classList.remove("active");
			form.classList.add("page-pass");
		});
	}

	// ── Secciones de Programas ────────────────────────────────────────────
	const secciones = {
		beneficios: document.querySelector("#section-beneficios"),
		prime:      document.querySelector("#section-prime"),
		afiliados:  document.querySelector("#section-afiliados"),
		trueke:     document.querySelector("#section-trueke"),
		servicios:  document.querySelector("#section-servicios"),
	};

	const parrafosDefault = document.querySelectorAll("#kd-dashboard .woocommerce-MyAccount-content > p");

	function updateActiveNavItem(section) {
		document.querySelectorAll("nav .custom-menu-item").forEach(item => {
			item.classList.toggle("is-active", item.dataset.section === section);
		});
	}

	function manejarVisibilidadProgramas(section) {
		const dash = document.querySelector("#kd-dashboard");
		if (dash) dash.classList.toggle("programas-activa", section === "programas");
	}

	function clearAllActive() {
		document.querySelectorAll(".kd-nav-item.kd-active").forEach(el => el.classList.remove("kd-active"));
	}

	function showSection(section) {
		Object.values(secciones).forEach(s => s && (s.style.display = "none"));
		parrafosDefault.forEach(p => p.style.display = "none");

		const wcContent = document.getElementById("kd-wc-content");

		if (section === "programas") {
			clearAllActive();
			cambiarProgramaActivo("beneficios");
			const progSub = document.querySelector(".kd-programas-sub");
			if (progSub) progSub.classList.remove("kd-sub-hidden");
			document.querySelector(".kd-item-programas")?.classList.add("kd-active");
			if (wcContent) wcContent.style.display = "none";
		} else if (secciones[section]) {
			clearAllActive();
			secciones[section].style.display = "flex";
			if (wcContent) wcContent.style.display = "none";
			document.querySelector(`.kd-item-${section}`)?.classList.add("kd-active");
		} else {
			parrafosDefault.forEach(p => p.style.display = "");
			if (wcContent) wcContent.style.display = "";
		}

		updateActiveNavItem(section);
		manejarVisibilidadProgramas(section);
	}

	function cambiarProgramaActivo(nombre) {
		document.querySelectorAll(".kd-prog-btn").forEach(btn => btn.classList.remove("active"));
		document.querySelector(".kd-prog-btn." + nombre)?.classList.add("active");
		Object.values(secciones).forEach(s => s && (s.style.display = "none"));
		if (secciones[nombre]) secciones[nombre].style.display = "flex";
	}

	document.querySelectorAll(".kd-prog-btn").forEach(btn => {
		btn.addEventListener("click", () => {
			const nombre = Array.from(btn.classList).find(c =>
				["beneficios","prime","afiliados","trueke","servicios"].includes(c)
			);
			if (nombre) cambiarProgramaActivo(nombre);
		});
	});

	document.querySelector(".kd-item-programas")?.addEventListener("click", () => {
		showSection("programas");
	});

	document.querySelector(".kd-item-servicios")?.addEventListener("click", () => {
		showSection("servicios");
	});

	function getQueryParam(param) {
		return new URLSearchParams(window.location.search).get(param);
	}

	const seccionInicial = getQueryParam("section") || "";
	showSection(seccionInicial);
});
</script>

<?php do_action( 'woocommerce_after_account_navigation' ); ?>
