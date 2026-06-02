<?php
/**
 * My Account page
 *
 * This template can be overridden by copying it to yourtheme/woocommerce/myaccount/my-account.php.
 *
 * HOWEVER, on occasion WooCommerce will need to update template files and you
 * (the theme developer) will need to copy the new files to your theme to
 * maintain compatibility. We try to do this as little as possible, but it does
 * happen. When this occurs the version of the template file will be bumped and
 * the readme will list any important changes.
 *
 * @see     https://woocommerce.com/document/template-structure/
 * @package WooCommerce\Templates
 * @version 3.5.0
 */

defined( 'ABSPATH' ) || exit;

/**
 * My Account navigation.
 *
 * @since 2.6.0
 */
?>
<style>
header.custom { 
	box-shadow: 0 0 0.5rem 0 rgba(0, 0, 0, 0.05);
}

/* ═══════════════════════════════════════════════
   KD DASHBOARD — Krear Dashboard
═══════════════════════════════════════════════ */
#kd-dashboard {
	background: #f2f2f2;
    padding: 1.5rem;
}
#kd-dashboard .ttl-user {
	display: none;
}
#kd-dashboard .wrapper  {
	max-width: 92rem;
}
#kd-dashboard .dash {
	display: grid;
	grid-template-columns: 260px 1fr;
	gap: 1rem;
	align-items: start;
}

/* ── Sidebar ── */
.kd-sidebar {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	position: sticky;
	top: 7.5rem;
	width: 100% !important;
}

/* ── Profile Card ── */
.kd-profile-card {
    background: #fff;
    border-radius: 1rem;
    padding: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: relative;
    overflow: hidden;
	box-shadow: 0 0.25rem 0.5rem rgb(0 0 0 / 5%);
}
.kd-profile-bg {
	border-radius: 0.75rem;
    height: 5rem !important;
}
.kd-deco {
    position: absolute;
    top: 0;
    right: 0;
    pointer-events: none;
    z-index: 0;
}

.kd-avatar-wrap {
    width: 4rem;
    height: 4rem;
    border-radius: 50%;
    box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.2);
    position: absolute;
    top: 3.25rem;
    left: 1.5rem;
}
.kd-avatar-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	border-radius: 100%;
}
.kd-avatar-default {
	padding: 12px;
}
.kd-avatar-dot {
    position: absolute;
    width: 1rem;
    height: 1rem;
    background-color: #15c26f;
    right: 0;
    bottom: 0;
    border: 3px solid #fff;
    border-radius: 50%;
}
.kd-name {
    font-weight: 700;
    font-size: 0.95rem;
    margin: 0;
    color: var(--secondary);
    line-height: 1.25rem;
    margin-top: 1.5rem;
    padding-left: 0.75rem;
}
.kd-username {
    font-size: 0.7rem;
    opacity: 0.4;
    margin: 0;
    margin-top: -0.85rem;
    line-height: 0.85rem;
    font-weight: 500;
    padding-left: 0.75rem;
    margin-bottom: 0.5rem;
}

/* ── Nav Card ── */
.kd-nav-card {
	background: #fff;
    border-radius: 1.5rem;
    padding: 1.5rem 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    box-shadow: 0 0.25rem 0.5rem rgb(0 0 0 / 5%);
}

/* ── Nav Items ── */
.kd-nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.25rem 1.75rem;
    cursor: pointer;
    color: var(--black);
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none !important;
    border-left: 3px solid transparent;
    transition: background 0.15s, color 0.15s, border-color 0.15s;
    position: relative;
}
.kd-nav-item:hover {
	opacity: 0.5;
}
.kd-nav-item.kd-active {
    color: var(--primary);
    font-weight: 600;
    border-left-color: var(--primary);
}
.kd-icon {
	width: 18px;
	height: 18px;
	flex-shrink: 0;
	stroke: currentColor;
}
.kd-item-salir { color: #999; margin-top: 0.25rem; border-top: 1px solid #f5f5f5; }
.kd-item-salir:hover { color: #c0392b; background: #fff5f5; border-left-color: #c0392b; }

/* ── Sub-items ── */
.kd-nav-sub {
	padding: 0.25rem 1.25rem 0.5rem 3.25rem;
	display: flex;
	flex-direction: column;
	gap: 0.2rem;
}
.kd-sub-hidden { display: none !important; }
.kd-sub-btn {
	background: none;
	border: none;
	text-align: left;
	padding: 0.45rem 0.6rem;
	border-radius: 8px;
	font-size: 0.83rem;
	color: #777;
	cursor: pointer;
	transition: background 0.15s, color 0.15s;
	font-weight: 500;
}
.kd-sub-btn:hover  { background: #f5f5f5; color: #333; }
.kd-sub-btn.active { background: #fdf3ee; color: #e05a00; font-weight: 700; }

/* ── Orders sub-list ── */
.kd-orders-sub {
	padding: 0.25rem 1.25rem 0.5rem 3.25rem;
	display: flex;
	flex-direction: column;
	gap: 0.2rem;
	max-height: 200px;
	overflow-y: auto;
}
.kd-order-link {
	font-size: 0.82rem;
	color: #777;
	text-decoration: none;
	padding: 0.4rem 0.6rem;
	border-radius: 8px;
	transition: background 0.15s;
}
.kd-order-link:hover, .kd-order-link.kd-sub-active {
	background: #fdf3ee;
	color: #e05a00;
}

/* ── Content area ── */
#kd-dashboard .woocommerce-MyAccount-content {
	background: #fff;
	border-radius: 16px;
	box-shadow: 0 2px 12px rgba(0,0,0,0.06);
	padding: 2rem;
	/* min-height: 500px; */
	width: 100% !important;
}

/* ── Content area ── */
#kd-dashboard .k3d-edit-profile {
	display: flex;
}
.k3d-edit-profile .edit-fields {
}
.k3d-edit-profile .form-row {
    padding: 0;
    margin: 0;
}
.k3d-edit-profile .form-row label {
    opacity: 0.5;
	font-weight: 500 !important;
    font-size: 0.8rem;
}
.k3d-edit-profile .form-row .input-text {
    font-weight: 500;
    font-family: inherit;
    font-size: 0.85rem;
    border: 1px solid #00000024;
    border-radius: 0.75rem;
    padding: 1rem;
}

/* Ocultar fieldset de contraseña inmediatamente para evitar flash */
#kd-wc-content .woocommerce-EditAccountForm fieldset { display: none; }

/* ── Responsive ── */
@media (max-width: 768px) {
	#kd-dashboard { padding: 1rem; }
	#kd-dashboard .dash {
		grid-template-columns: 1fr;
	}
	.kd-sidebar { position: static; }
}
</style>
<script>
(function() {
  const path = window.location.pathname.replace(/\/$/, '');
  if (path === '/mi-cuenta') {
    window.location.replace('/mi-cuenta/edit-account/');
  }
})();

document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("header")?.classList.add("custom");
});
</script>
<div id="kd-dashboard">
    <div class="ttl-user">
        <h1>Mi Perfil</h1>
    </div>
    <div class="wrapper">
		<div class="dash">
        <?php do_action( 'woocommerce_account_navigation' ); ?>
      <div class="woocommerce-MyAccount-content">
			
		  <div id="section-beneficios" class="section-content" style="display:none;">
			  <div class="logo">
				<img
				  src="/wp-content/uploads/2025/01/new-logo-beneficios-25-scaled.webp"
				  alt="imag"
				/>
			  </div>
			  <p class="intro">
				Tus compras se convierten en puntos para acceder a distintos niveles de
				experiencia y así obtener más descuentos iniciarás siendo un Novato y te
				esperarán muchos retos para subir de nivel. <br />
				¡Qué esperas para ser un Máster!
			  </p>
			  <div class="levels">
				<div class="title">
				  <p>Niveles de Experiencia</p>
				</div>
				<div class="fases">
				  <div class="imas">
					<div class="fase active">
					  <img
						src="/wp-content/uploads/2023/10/s0.svg"
						alt=""
					  />
					  <p>Novato</p>
					</div>
					<div class="fase">
					  <img
						src="/wp-content/uploads/2023/10/s2.svg"
						alt=""
					  />
					  <p>Maker</p>
					</div>
					<div class="fase">
					  <img
						src="/wp-content/uploads/2023/10/s3.svg"
						alt=""
					  />
					  <p>Pro</p>
					</div>
					<div class="fase">
					  <img
						src="/wp-content/uploads/2023/10/s4.svg"
						alt=""
					  />
					  <p>Master</p>
					</div>
				  </div>
				  <div class="bar">
					<span class="backline"></span>
					<div class="circle active">
					  <span class=""></span>
					</div>
					<span class="line"></span>
					<div class="circle">
					  <span></span>
					</div>
					<span class="line"></span>
					<div class="circle">
					  <span></span>
					</div>
					<span class="line"></span>
					<div class="circle">
					  <span></span>
					</div>
				  </div>
				</div>
			  </div>
			  <div class="puntos">
				<div class="title">
				  <p>PUNTOS EXTRA</p>
				</div>
				<div class="redes">
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/facebook-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en Facebook</span>
					<span class="p">100 puntos</span>
					<p class="ref">Krear 3D</p>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/instagram-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en Instagram</span>
					<span class="p">100 puntos</span>
					<p class="ref">@krear3d_peru</p>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/tiktok-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en Tik Tok</span>
					<span class="p">100 puntos</span>
					<p class="ref">@krear3d_peru</p>
				  </div>

				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/threads-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en Threads</span>
					<span class="p">100 puntos</span>
					<p class="ref">@krear3d_peru</p>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/x-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en X</span>
					<span class="p">100 puntos</span>
					<p class="ref">@krear3d_peru</p>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/facegroup-logo-b.webp"
					  alt=""
					/>
					<span class="s">Síguenos en nuestro grupo de Facebook</span>
					<span class="p">100 puntos</span>
					<p class="ref">Impresoras 3D Perú</p>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/whatsapp-logo-b3.webp"
					  alt=""
					/>
					<span class="s">Únete a nuestro canal de Whatsapp</span>
					<span class="p">100 puntos</span>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/opinion-logo-b.webp"
					  alt=""
					/>
					<span class="s">Deja una reseña en nuestra Web</span>
					<span class="p">100 puntos</span>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/googleop-logo-b.webp"
					  alt=""
					/>
					<span class="s">Deja una reseña en Google</span>
					<span class="p">200 puntos</span>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/cumple-logo-b4.webp"
					  alt=""
					/>
					<span class="s">Cumpleaños</span>
					<span class="p">200 puntos</span>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/estudiante-logo-b.webp"
					  alt=""
					/>
					<span class="s">Bono para estudiantes</span>
					<span class="p">200 puntos</span>
				  </div>
				  <div class="red">
					<img
					  class="icon"
					  src="/wp-content/uploads/2024/10/afiliados-logo-b.webp"
					  alt=""
					/>
					<span class="s">Refiere a un amigo +1</span>
					<span class="p">300 puntos</span>
				  </div>
				</div>
			  </div>
			  <div class="link">
				<p>REGÍSTRATE</p>
				<a href="/beneficios/">AQUÍ</a>
			  </div>
			</div>

			<div id="section-prime" class="section-content"  style="display:none;">
				 <div class="pasos">
					<div class="ps1">
					  <p>
						¿CÓMO SOY <br /><img
						  src="/wp-content/uploads/2024/11/prime-logo-white.webp"
						  alt=""
						/>?
					  </p>
					  <p>
						Aquí encontrarás el paso a paso de como suscribirte<br />
						y aprovechar todos los beneficios.
					  </p>
					</div>
					<div class="ps2">
					  <div class="line"></div>
					  <div class="n">
						<p>1</p>
						<div>
						  <p>Paso 1</p>
						  <p>
							Selecciona el plan de tu preferencia teniendo en cuenta los
							beneficios, marcas, precios y dale clic en ¡Hazte Prime!
						  </p>
						</div>
					  </div>
					  <div class="n">
						<p>2</p>
						<div>
						  <p>Paso 2</p>
						  <p>
							Serás redirigido a una interfaz donde deberás completar tus
							datos e introducir la información de tu tarjeta de crédito o
							débito para suscribirte.
						  </p>
						</div>
					  </div>
					  <div class="n">
						<p>3</p>
						<div>
						  <p>Paso 3</p>
						  <p>
							Recibirás un correo de bienvenida con el que podrás ponerte en
							contacto con un asesor comercial para aplicar tus beneficios.
						  </p>
						</div>
					  </div>
					</div>
				  </div>
				  <div class="benef">
					<div class="content-b">
					  <div>
						<img
						  src="/wp-content/uploads/2024/11/prime-bono1.webp"
						  alt=""
						/>
						<p>Kit de Bienvenida</p>
						<p>al programa prime</p>
					  </div>
					  <div>
						<img
						  src="/wp-content/uploads/2024/11/prime-bono2.webp"
						  alt=""
						/>
						<p>Descuentos especiales</p>
						<p>en insumos</p>
					  </div>
					  <div>
						<img
						  src="/wp-content/uploads/2024/11/prime-cumple.webp"
						  alt=""
						/>
						<p>Bono</p>
						<p>de cumpleaños</p>
					  </div>
					  <div>
						<img
						  src="/wp-content/uploads/2024/11/prime-pas6z1.webp"
						  alt=""
						/>
						<p>Entregas</p>
						<p>prioritarias</p>
					  </div>
					  <div>
						<img
						  src="/wp-content/uploads/2024/11/prime-bono4.webp"
						  alt=""
						/>
						<p>Mantenimiento</p>
						<p>gratuito</p>
					  </div>
					</div>
				  </div>
				  <div class="desc-planes">
					<div class="text">
					  <p>MARCAS</p>
					  <p>
						Con las que podrás<br />
						disfrutar los descuentos,<br />
						precios especiales y muchos<br />
						más...
					  </p>
					</div>
					<div class="marcas">
					  <p class="tfull">Plan Full</p>

					  <div class="plan-lite">
						<p class="tlite">Plan Lite</p>
						<img
						  src="/wp-content/uploads/2024/08/k3dlogo.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/krear3dlogo.webp"
						  alt=""
						/>
					  </div>
					  <div>
						<img
						  src="/wp-content/uploads/2024/08/anycubiclogo.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/esunlogo.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/10/logo-panchroma.svg"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/polymakerlogo.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/07/sunlu.png"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/phrozenlogo.webp"
						  alt=""
						/>
					  </div>

					  <div>
						<img
						  src="/wp-content/uploads/2024/08/bambu.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/elegoologo.webp"
						  alt=""
						/>
						<img
						  src="/wp-content/uploads/2024/08/crealityLogo.webp"
						  alt=""
						/>
					  </div>
					</div>
				  </div>
				  <div class="redir">
					<a href="/prime/">¡Hazte Prime!</a>
				  </div>
			</div>
			<div id="section-afiliados" class="section-content"  style="display:none;">
				<section class="data1-afi">
				<div class="info">
				  <h1>SÚMATE A ESTA REVOLUCIÓN</h1>
				  <p>
					Si eres youtuber, influencer, profesor o incluso aficionado comienza
					a ganar comisiones vendiendo de forma digital los productos de
					nuestra web entre tus amigos, seguidores o suscriptores con cero
					inversión y sin salir de tu casa. En Krear 3D estamos buscando
					afiliados que compartan nuestra pasión por las impresoras 3D y el
					mundo de la tecnología 3D para ofrecerles los siguientes beneficios:
				  </p>
				</div>

				<div class="cards">
				  <div class="card">
					<img
					  src="/wp-content/uploads/2024/06/respaldo.png"
					  alt=""
					/>
					<h1>COMISIONES Y RESPALDO</h1>
					<p>
					  Vende y gana 5% sobre los pedidos, nosotros nos encargamos del
					  resto (entrega, soporte, garantía, facturación, etc.)
					</p>
				  </div>

				  <div class="card">
					<img
					  src="/wp-content/uploads/2024/06/tec_confiable.png"
					  alt=""
					/>
					<h1>TECNOLOGÍA CONFIABLE</h1>
					<p>
					  Accede al portal exclusivo con reportes y seguimiento de tus
					  clientes por hasta 30 días para que efectúen su compra.
					</p>
				  </div>

				  <div class="card">
					<img
					  src="/wp-content/uploads/2024/06/valor_agregadox1.png"
					  alt=""
					/>
					<h1>VALOR AGREGADO</h1>
					<p>
					  Promociona los productos de Krear 3D para mejorar tu canal, página
					  o red social con tecnologías innovadoras y marcas reconocidas.
					</p>
				  </div>
				</div>
			  </section>
			  <section class="video-ins">
				<iframe
				  id="youtube-video"
				  src="https://www.youtube.com/embed/dREtPFx0a2M?si=no4pT7twNKitC-DR&amp;autoplay=1&amp;mute=1"
				  title="Afiliados Krear3D"
				  frameborder="0"
				  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
				  referrerpolicy="strict-origin-when-cross-origin"
				  allowfullscreen=""
				></iframe>
			  </section>
			  <section class="unete">
				<div>
				  <p>¡Únete a nuestro programa!</p>
				  <h1>AHORA</h1>
				</div>

				<div>
				  <a href="/afiliados/"><button>AFÍLIATE AQUÍ</button></a>
				</div>
			  </section>
		  	</div>
		  
			<div id="section-servicios" class="section-content servicios-section" style="display:none;">
			<?php
			$current_user    = wp_get_current_user();
			$wp_user_id      = get_current_user_id();
			$wp_user_email   = $current_user->user_email;
			$wp_user_display = $current_user->display_name;
			$wp_user_phone   = get_user_meta( $wp_user_id, 'billing_phone', true );
			$wp_user_dni     = get_user_meta( $wp_user_id, 'billing_dni', true );
			?>
			<div class="servicios-header">
				<h2>Beneficios exclusivos</h2>
				<p>Accede a nuestros servicios especiales para clientes Krear 3D.</p>
			</div>

			<div class="servicios-cards">
				<div class="servicio-card" data-type="curso-fdm">
					<div class="top">
						<div class="data">
							<span>Curso online</span>
							<div class="title">Impresión 3D</div>
							<div class="type">FDM</div>
							<p>Introducción a la impresión 3D, uso de impresoras FDM y sus aplicaciones.</p>
							<ul>
								<li><b></b>Preparación y mantenimiento</li>
								<li><b></b>Software de laminado</li>
								<li><b></b>Uso correcto de filamentos</li></ul>
						</div>

						<div class="image">
							<img src="https://www.tiendakrear3d.com/wp-content/uploads/2026/05/fdm.webp">
						</div>
					</div>

					<div class="bottom">
						<div class="icon">
							<svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="512" height="512" x="0" y="0" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512" xml:space="preserve" class=""><g transform="matrix(0.8500000000000008,0,0,0.8500000000000008,38.399999427795166,38.39999885559058)"><path d="M130 161c-30.918 0-45 49.245-45 95s14.082 95 45 95 45-49.245 45-95-14.082-95-45-95zm0 159.359c-5.216-4.926-15-26.749-15-64.359s9.784-59.434 15-64.359c5.216 4.926 15 26.749 15 64.359s-9.784 59.434-15 64.359z" fill="#ea7134" opacity="1" data-original="#000000" class=""></path><path d="M476.855 432.873C499.519 385.377 512 322.563 512 256s-12.481-129.377-35.145-176.873C452.507 28.101 418.819 0 382 0c-42.206 0-79.849 36.664-104.163 101h-43.676c-2.88-7.594-5.98-14.902-9.306-21.873C200.506 28.101 166.82 0 130 0S59.494 28.101 35.145 79.127C12.481 126.623 0 189.437 0 256s12.481 129.377 35.145 176.873C59.494 483.899 93.18 512 130 512s70.506-28.101 94.855-79.127c3.326-6.97 6.426-14.279 9.306-21.873h43.676C302.151 475.336 339.794 512 382 512c17.236 0 33.785-6.159 49.011-17.944C455.634 505.559 483.077 512 512 512v-30c-20.566 0-40.244-3.861-58.361-10.881 8.413-10.769 16.204-23.551 23.216-38.246zm-279.076-12.92C178.963 459.385 154.259 482 130 482c-24.259 0-48.963-22.615-67.779-62.047C41.443 376.41 30 318.184 30 256S41.443 135.59 62.221 92.047C81.037 52.615 105.741 30 130 30c24.259 0 48.963 22.615 67.779 62.047C218.557 135.59 230 193.816 230 256s-11.443 120.41-32.221 163.953zM243.947 381C254.415 343.31 260 300.497 260 256s-5.585-87.31-16.054-125H297.4c2.645 2.589 8.859 12.664 14.294 37.353C317.051 192.678 320 223.806 320 256v64c0 21.315 3.497 41.827 9.938 61h-85.991zM382 482c-14.385 0-28.556-7.535-42.122-22.396-11.061-12.118-21.162-28.709-29.689-48.604h32.784c14.229 26.323 34.428 48.96 58.77 66.095C395.213 480.318 388.591 482 382 482zm-43.064-328.736c-2.171-8.43-4.604-15.868-7.267-22.264h31.735c2.648 2.598 8.86 12.682 14.291 37.352C383.051 192.678 386 223.806 386 256c0 32.194-2.949 63.322-8.306 87.648-5.431 24.67-11.643 34.754-14.291 37.352h-1.47C354.248 362.162 350 341.569 350 320v-64c0-38.546-3.93-75.032-11.064-102.736zm87.183 304.037a163.274 163.274 0 0 1-49.867-48.993c5.072-2.532 10.516-7.218 15.556-15.538 5.035-8.313 9.452-19.763 13.128-34.034C412.07 331.032 416 294.546 416 256c0-38.546-3.93-75.032-11.064-102.736-3.676-14.271-8.093-25.721-13.128-34.034-9.127-15.068-19.582-18.23-26.745-18.23H310.19c8.526-19.896 18.627-36.487 29.688-48.604C353.444 37.535 367.615 30 382 30c24.259 0 48.964 22.615 67.779 62.047C470.558 135.59 482 193.816 482 256s-11.442 120.41-32.221 163.953c-7.151 14.987-15.155 27.538-23.66 37.348z" fill="#ea7134" opacity="1" data-original="#000000" class=""></path></g></svg>
						</div>
						<p>Ideal para prototipos, pieza funcionales y proyectos de uso diario.</p>
						<div class="action">Acceder al curso</div>
					</div>
				</div>

				<div class="servicio-card" data-type="curso-lcd">
					<div class="top">
						<div class="data">
							<span>Curso online</span>
							<div class="title">Impresión 3D</div>
							<div class="type">LCD</div>
							<p>Curso de impresión 3D en resina, enfocado en precisión, materiales y postprocesado.</p>
							<ul>
								<li><b></b>Impresión, uso y seguridad</li>
								<li><b></b>Software y soportes</li>
								<li><b></b>Tipos de resina</li></ul>
						</div>

						<div class="image">
							<img src="https://www.tiendakrear3d.com/wp-content/uploads/2026/05/lcd.webp">
						</div>
					</div>

					<div class="bottom">
						<div class="icon">
							<svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="512" height="512" x="0" y="0" viewBox="0 0 513.398 513.398" style="enable-background:new 0 0 512 512" xml:space="preserve" class=""><g><path d="M414.315 19.258H99.112L0 154.41l257.764 339.73 255.635-339.769zm-273.4 150 72.622 216.961L48.922 169.258zm31.637 0h168.412l-83.628 253.297zm200.006 0h92.098L300.541 387.385zm26.553-120 66 90h-92.533l-29.531-90zm-87.638 0 29.531 90H172.422l29.531-90zm-197.159 0h56.064l-29.531 90H48.314z" fill="#ea7134" opacity="1" data-original="#000000" class=""></path></g></svg>
						</div>
						<p>Ideal para miniaturas, joyería, dental, modelismo y alta precisión.</p>
						<div class="action">Acceder al curso</div>
					</div>
				</div>

				<!-- <div class="servicio-card" data-type="stl">
					<div class="servicio-icon">
						<img src="/wp-content/uploads/2025/07/cuenta.png" alt="STL" class="servicio-img-icon">
					</div>
					<h3>K3D FAB</h3>
					<p class="servicio-desc">Accede a nuestra biblioteca de archivos STL exclusivos para impresión 3D.</p>
					<div class="servicio-action">
						<span class="servicio-status-badge" style="display:none;"></span>
						<button class="btn-solicitar" data-type="stl">Solicitar acceso</button>
						<a class="btn-acceder" data-type="stl" href="#" target="_blank" style="display:none;">Acceder</a>
					</div>
				</div> -->

			</div>

			<!-- Modal: datos de perfil faltantes -->
			<div id="modal-perfil-servicio" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
				<div style="background:#fff; border-radius:12px; padding:2rem; max-width:400px; width:90%; position:relative;">
					<button id="modal-perfil-close" style="position:absolute; top:1rem; right:1rem; background:none; border:none; font-size:1.4rem; cursor:pointer;">&times;</button>
					<h3 style="margin-bottom:0.5rem;">Completa tus datos</h3>
					<p style="margin-bottom:1.2rem; color:#666; font-size:0.9rem;">Necesitamos tus datos y el comprobante (boleta o factura) para procesar tu solicitud.</p>
					<input type="hidden" id="modal-servicio-type" value="">
					<div id="perfil-fields">
					<div style="margin-bottom:1rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">Teléfono</label>
						<input type="tel" id="input-phone" placeholder="Ej: 987654321" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
					</div>
					<div style="margin-bottom:1.5rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">DNI</label>
						<input type="text" id="input-dni" placeholder="Ej: 12345678" maxlength="8" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
					</div>
					</div>
					<div style="margin-bottom:1rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">N° de boleta / factura</label>
						<input type="text" id="input-invoice" placeholder="Ej: B001-12345" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
					</div>
					<div style="margin-bottom:1.5rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">Boleta / factura (imagen o PDF)</label>
						<input type="file" id="input-voucher" accept="image/*,application/pdf" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box; background:#fff;">
					</div>
					<button id="modal-perfil-submit" style="width:100%; padding:12px; background:#e05a00; color:#fff; border:none; border-radius:8px; font-weight:700; font-size:1rem; cursor:pointer;">Enviar solicitud</button>
					<p id="modal-perfil-error" style="color:red; margin-top:0.7rem; display:none;"></p>
				</div>
			</div>

			<style>
			.servicios-section {
				flex-direction: column;
				gap: 1.5rem;
			}
			.servicios-header h2 { margin: 0 0 0.3rem; font-size: 1.4rem; }
			.servicios-header p { color: #666; margin: 0; }
			.servicios-cards { display: flex; flex-wrap: wrap; gap: 1.5rem; }
			
			.servicio-card {
				background: #fff;
				border: 1px solid #eee;
				border-radius: 12px;
				padding: 1.5rem;
				flex: 1 1 220px;
				display: flex;
				flex-direction: column;
				width: 50%;
				gap: 0.8rem;
				box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
				overflow: hidden;
			}
			.servicio-card .top {
				display: flex;
			}
			.servicio-card .top .data {
				display: flex;
				flex-direction: column;
				align-items: start;
				gap: 0.25rem;
			}
			.servicio-card .top .data span {
				background: var(--primaryopacity);
				color: var(--primary);
				font-size: 0.7rem;
				font-weight: 700;
				padding: 0.25rem 0.75rem;
				border-radius: 1rem;
			}
			.servicio-card .top .data .title {
				font-size: 1.2rem;
				font-weight: 800;
				margin-top: 0.25rem;
			}
			.servicio-card .top .data .type {
				font-size: 1.2rem;
				font-weight: 800;
				color: var(--primary);
				margin-top: -0.5rem;
			}
			.servicio-card .top .data p {
				font-size: 0.75rem;
				font-weight: 500;
				margin-top: -0.125rem;
				margin-bottom: 0.75rem;
				max-width: 75%;
			}
			.servicio-card .top .data ul {
				font-size: 0.7rem;
				font-weight: 500;
				display: flex;
				flex-direction: column;
				gap: 0.4rem;
			}
			.servicio-card .top .data ul li {
				display: flex;
				gap: 0.5rem;
				align-items: center;
			}
			.servicio-card .top .data ul li b {
				width: 0.75rem;
				height: 0.75rem;
				display: block;
				background-color: var(--primary);
				border-radius: 1rem;
			}
			.servicio-card .top .image {
				max-width: 12rem;
				margin-right: -0.5rem;
				display: flex;
				align-items: end;
				justify-content: end;
			}
			.servicio-card .top .image img {
				width: 90%;
			}
			.servicio-card .bottom {
				color: var(--primary);
				margin: 0 -1rem -1rem -1rem;
				display: flex;
				padding: 0.75rem 1rem;
				justify-content: space-between;
				gap: 1rem;
				align-items: center;
			}
			.servicio-card .bottom .icon {
				display: flex;
				align-items: center;
				background-color: #ea713433;
				width: 2.5rem;
				min-width: 2.5rem;
				height: 2.5rem;
				border-radius: 2rem;
				justify-content: center;
			}
			.servicio-card .bottom .icon svg {
				width: 1.5rem;
				height: 1.5rem;
			}
			.servicio-card .bottom p {
				font-size: 0.7rem;
				line-height: 1.15rem;
				margin: 0;
				font-weight: 500;
				opacity: 0.75;
			}
			.servicio-card .bottom .action {
				background-color: var(--primary);
				color: white;
				align-items: center;
				justify-content: center;
				display: flex;
				padding: 0.5rem 1rem;
				border-radius: 0.5rem;
				white-space: nowrap;
				font-weight: 500;
				margin-right: 0.25rem;
			}

			.servicio-desc { color: #555; font-size: 0.9rem; margin: 0; }
			.servicio-img-icon { width: 48px; height: 48px; object-fit: contain; }
			.servicio-action { display: flex; flex-direction: column; gap: 0.5rem; margin-top: auto; }
			.btn-solicitar {
				padding: 10px 16px;
				background: #e05a00;
				color: #fff;
				border: none;
				border-radius: 8px;
				font-weight: 700;
				cursor: pointer;
				transition: opacity 0.2s;
			}
			.btn-solicitar:disabled { opacity: 0.5; cursor: not-allowed; }
			.btn-acceder {
				display: inline-block;
				padding: 10px 16px;
				background: #1a7a1a;
				color: #fff !important;
				border-radius: 8px;
				font-weight: 700;
				text-align: center;
				text-decoration: none;
			}
			.servicio-status-badge {
				font-size: 0.8rem;
				padding: 4px 10px;
				border-radius: 20px;
				font-weight: 600;
				display: inline-block;
			}
			.badge-pending { background: #fff3cd; color: #856404; }
			.badge-approved { background: #d1e7dd; color: #0a3622; }
			.badge-rejected { background: #f8d7da; color: #842029; }
			.servicio-card .bottom .action { cursor: pointer; transition: opacity 0.15s; }
			.servicio-card .bottom .action:hover { opacity: 0.9; }
			.servicio-card .bottom .action.is-pending { background-color: #9ca3af; cursor: default; }
			.servicio-card .bottom .action.is-pending:hover { opacity: 1; }
			.servicio-card .bottom .action.is-rejected { background-color: #dc3545; cursor: default; }
			.servicio-card .bottom .action.is-rejected:hover { opacity: 1; }
			</style>

			<script>
            (function() {
                const API        = 'https://devapi.krear3d.com';
                const PLATFORM   = 'https://cursos.krear3d.com/';
                const WP_USER_ID = <?php echo (int) $wp_user_id; ?>;
                const WP_EMAIL   = <?php echo json_encode( $wp_user_email ); ?>;
                const WP_USERNAME = <?php echo json_encode( $wp_user_display ); ?>;
                const WP_PHONE   = <?php echo json_encode( $wp_user_phone ?: '' ); ?>;
                const WP_DNI     = <?php echo json_encode( $wp_user_dni ?: '' ); ?>;

                const TYPES = ['curso-fdm', 'curso-lcd'];
                let cachedProfile = null;

                async function fetchProfile() {
                    if (cachedProfile !== null) return cachedProfile;
                    try {
                        const r = await fetch(`${API}/approval/wp_profile/${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
                        const j = await r.json();
                        cachedProfile = j.data || {};
                    } catch(e) { cachedProfile = {}; }
                    return cachedProfile;
                }

                async function checkStatuses() {
                    for (const type of TYPES) {
                        try {
                            const r = await fetch(`${API}/approval/status?wp_user_id=${WP_USER_ID}&type=${type}`, { headers: { 'X-No-Toast': '1' } });
                            const j = await r.json();
                            applyStatus(type, j.data || {});
                        } catch(e) {}
                    }
                }

                function applyStatus(type, data) {
                    const card = document.querySelector(`.servicio-card[data-type="${type}"]`);
                    if (!card) return;
                    const action = card.querySelector('.action');
                    if (!action) return;

                    const status = data.status || 'none';
                    card.dataset.state     = status;
                    card.dataset.accessUrl = data.access_url || PLATFORM;

                    action.classList.remove('is-pending', 'is-rejected');
                    if (status === 'approved') {
                        action.textContent = 'Acceder al curso';
                    } else if (status === 'pending' || status === 'in_review') {
                        action.textContent = 'En revisión';
                        action.classList.add('is-pending');
                    } else if (status === 'rejected') {
                        action.textContent = 'Solicitud rechazada';
                        action.classList.add('is-rejected');
                    } else {
                        action.textContent = 'Solicitar acceso';
                    }
                }

                function onActionClick(card) {
                    const state = card.dataset.state || 'none';
                    const type  = card.dataset.type;
                    if (state === 'approved') {
                        window.open(card.dataset.accessUrl || PLATFORM, '_blank');
                    } else if (state === 'pending' || state === 'in_review' || state === 'rejected') {
                        /* en revisión / rechazado: sin acción */
                    } else {
                        handleSolicitar(type);
                    }
                }

                async function submitRequest(type, phone, dni, invoiceNumber, file) {
                    const fd = new FormData();
                    fd.append('wp_user_id',     WP_USER_ID);
                    fd.append('type_slug',      type);
                    fd.append('email',          WP_EMAIL);
                    fd.append('phone',          phone);
                    fd.append('dni',            dni);
                    fd.append('wp_username',    WP_USERNAME);
                    fd.append('invoice_number', invoiceNumber);
                    fd.append('voucher',        file);
                    const r = await fetch(`${API}/approval/request`, {
                        method: 'POST',
                        body:   fd,
                    });
                    return r.json();
                }

                async function handleSolicitar(type) {
                    const profile = await fetchProfile();
                    const phone = profile.phone || WP_PHONE;
                    const dni   = profile.dni   || WP_DNI;
                    const known = !!(profile.phone && profile.dni); // ya tiene datos guardados
                    openModal(type, phone, dni, known);
                }

                async function doSubmit(type, phone, dni, invoiceNumber, file) {
                    if (!phone || !dni) return;
                    if (!WP_EMAIL) { alert('No se encontró tu correo electrónico.'); return; }
                    cachedProfile = { phone, dni, email: WP_EMAIL };
                    await submitRequest(type, phone, dni, invoiceNumber, file);
                    closeModal();
                    await checkStatuses();
                }

                function openModal(type, existingPhone, existingDni, known) {
                    document.getElementById('modal-servicio-type').value = type;
                    document.getElementById('input-phone').value = existingPhone || '';
                    document.getElementById('input-dni').value   = existingDni   || '';
                    document.getElementById('input-invoice').value = '';
                    document.getElementById('input-voucher').value = '';
                    document.getElementById('perfil-fields').style.display = known ? 'none' : 'block';
                    document.getElementById('modal-perfil-error').style.display = 'none';
                    document.getElementById('modal-perfil-servicio').style.display = 'flex';
                }

                function closeModal() {
                    document.getElementById('modal-perfil-servicio').style.display = 'none';
                }

                document.addEventListener('DOMContentLoaded', function() {
                    checkStatuses();

                    document.querySelectorAll('.servicio-card[data-type^="curso-"]').forEach(card => {
                        const action = card.querySelector('.action');
                        if (action) action.addEventListener('click', () => onActionClick(card));
                    });

                    document.getElementById('modal-perfil-close').addEventListener('click', closeModal);

                    document.getElementById('modal-perfil-submit').addEventListener('click', async function() {
                        const type  = document.getElementById('modal-servicio-type').value;
                        const phone   = document.getElementById('input-phone').value.trim();
                        const dni     = document.getElementById('input-dni').value.trim();
                        const invoice = document.getElementById('input-invoice').value.trim();
                        const file    = document.getElementById('input-voucher').files[0];
                        const errEl   = document.getElementById('modal-perfil-error');
                        const perfilVisible = document.getElementById('perfil-fields').style.display !== 'none';

                        if (perfilVisible) {
                            if (!phone || !dni) {
                                errEl.textContent = 'Por favor ingresa tu teléfono y DNI.';
                                errEl.style.display = 'block';
                                return;
                            }
                            if (!/^\d{8}$/.test(dni)) {
                                errEl.textContent = 'El DNI debe tener 8 dígitos.';
                                errEl.style.display = 'block';
                                return;
                            }
                        }
                        if (!invoice) {
                            errEl.textContent = 'Ingresa el número de boleta o factura.';
                            errEl.style.display = 'block';
                            return;
                        }
                        if (!file) {
                            errEl.textContent = 'Adjunta la boleta o factura (imagen o PDF).';
                            errEl.style.display = 'block';
                            return;
                        }
                        if (!/\.(pdf|png|jpe?g|webp)$/i.test(file.name)) {
                            errEl.textContent = 'El archivo debe ser una imagen o PDF.';
                            errEl.style.display = 'block';
                            return;
                        }
                        errEl.style.display = 'none';
                        this.disabled = true;
                        this.textContent = 'Enviando...';
                        await doSubmit(type, phone, dni, invoice, file);
                        this.disabled = false;
                        this.textContent = 'Enviar solicitud';
                    });

                    document.getElementById('modal-perfil-servicio').addEventListener('click', function(e) {
                        if (e.target === this) closeModal();
                    });
                });
            })();
            </script>
		  </div>

		  <!-- ═══════════ GUÍAS ═══════════ -->
		  <div id="section-guias" class="section-content guias-section" style="display:none;">
			<?php
			$gwa_user_id    = get_current_user_id();
			$gwa_user_email = wp_get_current_user()->user_email;
			$gwa_user_phone = get_user_meta( $gwa_user_id, 'billing_phone', true );
			$gwa_user_dni   = get_user_meta( $gwa_user_id, 'billing_dni', true );
			?>

			<div class="guias-header">
				<h2>Mis Equipos</h2>
				<p>Accede a las guías de los equipos que has adquirido.</p>
			</div>

			<!-- Grid de equipos aprobados + card de agregar -->
			<div class="guias-grid" id="guias-grid">
				<!-- Las cards aprobadas se insertan aquí via JS -->
				<div class="guia-add-card" id="guia-add-btn">
					<div class="guia-add-icon">+</div>
					<span>Agregar equipo</span>
				</div>
			</div>

			<!-- Detalle del equipo seleccionado -->
			<div class="guia-detail-wrap" id="guia-detail-wrap" style="display:none;">
				<button class="guia-back-btn" id="guia-back-btn">← Volver</button>
				<div class="guia-detail-header">
					<img id="guia-detail-img" src="" alt="" width="72" height="72">
					<div>
						<div class="guia-detail-name" id="guia-detail-name"></div>
						<div class="guia-detail-brand" id="guia-detail-brand"></div>
					</div>
				</div>
				<div class="guia-detail-desc" id="guia-detail-desc"></div>
				<div class="guia-detail-items" id="guia-detail-items"></div>
			</div>

			<!-- Modal: solicitar guía -->
			<div id="modal-guia-request" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
				<div class="guia-modal-inner">
					<button id="modal-guia-close" class="guia-modal-close">&times;</button>
					<h3>Solicitar guía de equipo</h3>
					<p class="guia-modal-sub">Busca tu equipo y adjunta tu boleta o factura de compra.</p>

					<!-- Búsqueda de equipo -->
					<div class="guia-search-wrap">
						<div class="guia-search-field">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
							<input type="text" id="guia-machine-input" placeholder="Escribe el modelo del equipo..." autocomplete="off">
						</div>
						<div id="guia-machine-list" class="guia-machine-list" style="display:none;"></div>
						<div id="guia-machine-selected" class="guia-machine-selected" style="display:none;">
							<img id="guia-sel-img" src="" alt="" width="40" height="40">
							<span id="guia-sel-name"></span>
							<button id="guia-sel-clear">✕</button>
						</div>
					</div>

					<!-- Adjuntar comprobante -->
					<div class="guia-upload-wrap">
						<label class="guia-upload-label" id="guia-upload-label">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
							<span id="guia-upload-text">Adjuntar boleta / factura (PDF o imagen)</span>
							<input type="file" id="guia-voucher-input" accept=".pdf,.jpg,.jpeg,.png,.webp" style="display:none">
						</label>
					</div>

					<!-- Datos de contacto (solo si faltan en el perfil) -->
					<div id="guia-profile-fields" style="display:none;">
						<p style="font-size:0.82rem;color:#888;margin:0 0 0.8rem;">Necesitamos tu teléfono y DNI para la solicitud. Solo te lo pedimos esta vez.</p>
						<div class="guia-field">
							<label>Teléfono</label>
							<input type="tel" id="guia-phone-input" placeholder="Ej: 987654321">
						</div>
						<div class="guia-field">
							<label>DNI</label>
							<input type="text" id="guia-dni-input" placeholder="Ej: 12345678" maxlength="8">
						</div>
					</div>

					<p id="guia-request-error" style="color:red;display:none;margin-top:0.5rem;font-size:0.85rem;"></p>
					<button id="guia-request-submit" class="guia-submit-btn">Enviar solicitud</button>
				</div>
			</div>

			<style>
			.guias-section { flex-direction: column; gap: 1.5rem; padding: 1.5rem; }
			.guias-header h2 { margin: 0 0 0.3rem; font-size: 1.4rem; }
			.guias-header p  { color: #666; margin: 0; font-size: 0.9rem; }

			.guias-grid {
				display: flex;
				flex-wrap: wrap;
				gap: 1.2rem;
			}
			.guia-card {
				background: #fff;
				border: 1px solid #eee;
				border-radius: 14px;
				padding: 1.2rem;
				width: 160px;
				display: flex;
				flex-direction: column;
				align-items: center;
				gap: 0.6rem;
				cursor: pointer;
				box-shadow: 0 2px 8px rgba(0,0,0,0.06);
				transition: transform 0.15s, box-shadow 0.15s;
				text-align: center;
			}
			.guia-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
			.guia-card img { width: 72px; height: 72px; object-fit: contain; border-radius: 8px; background: #f9f9f9; }
			.guia-card-brand { font-size: 0.7rem; opacity: 0.45; font-weight: 600; text-transform: uppercase; }
			.guia-card-name  { font-size: 0.85rem; font-weight: 700; color: #222; line-height: 1.2; }

			.guia-card-pending { opacity: 0.75; cursor: default; }
			.guia-card-pending:hover { transform: none; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
			.guia-badge-pending {
				font-size: 0.7rem; font-weight: 700;
				background: #fff3cd; color: #856404;
				padding: 3px 10px; border-radius: 20px;
				align-self: center;
			}

			.guia-add-card {
				background: #f9f9f9;
				border: 2px dashed #ddd;
				border-radius: 14px;
				padding: 1.2rem;
				width: 160px;
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				gap: 0.5rem;
				cursor: pointer;
				transition: background 0.15s, border-color 0.15s;
				min-height: 140px;
			}
			.guia-add-card:hover { background: #f0f0f0; border-color: #e05a00; }
			.guia-add-icon {
				font-size: 2rem;
				color: #e05a00;
				line-height: 1;
			}
			.guia-add-card span { font-size: 0.82rem; color: #888; font-weight: 600; }

			/* Detail */
			.guia-detail-wrap { display: flex; flex-direction: column; gap: 1rem; }
			.guia-back-btn {
				background: none; border: none; cursor: pointer;
				color: #e05a00; font-weight: 700; font-size: 0.9rem;
				padding: 0; align-self: flex-start;
			}
			.guia-detail-header {
				display: flex; align-items: center; gap: 1rem;
				padding: 1rem; background: #f9f9f9; border-radius: 12px;
			}
			.guia-detail-header img { object-fit: contain; border-radius: 8px; background: #fff; }
			.guia-detail-name  { font-size: 1.15rem; font-weight: 700; }
			.guia-detail-brand { font-size: 0.78rem; opacity: 0.5; margin-top: 2px; }
			.guia-detail-desc  { color: #444; font-size: 0.9rem; line-height: 1.6; white-space: pre-line; }

			.guia-detail-items { display: flex; flex-direction: column; gap: 1rem; }
			.guia-item-card {
				border: 1px solid #eee;
				border-radius: 10px;
				padding: 0.8rem 1rem;
				display: flex;
				flex-direction: column;
				gap: 0.4rem;
			}
			.guia-item-title { font-weight: 600; font-size: 0.9rem; }
			.guia-item-card img { max-width: 100%; border-radius: 8px; }
			.guia-item-link {
				color: #e05a00; text-decoration: none; font-weight: 600;
				font-size: 0.88rem; display: inline-flex; align-items: center; gap: 0.3rem;
			}
			.guia-item-link:hover { text-decoration: underline; }

			/* Modal */
			.guia-modal-inner {
				background: #fff; border-radius: 16px; padding: 1.8rem;
				max-width: 460px; width: 90%; position: relative;
				max-height: 90vh; overflow-y: auto;
			}
			.guia-modal-inner h3 { margin: 0 0 0.3rem; font-size: 1.15rem; }
			.guia-modal-sub { color: #666; font-size: 0.88rem; margin: 0 0 1.2rem; }
			.guia-modal-close {
				position: absolute; top: 1rem; right: 1rem;
				background: none; border: none; font-size: 1.4rem; cursor: pointer; color: #999;
			}

			.guia-search-wrap { position: relative; margin-bottom: 1rem; }
			.guia-search-field {
				display: flex; align-items: center; gap: 0.5rem;
				border: 1.5px solid #ddd; border-radius: 10px; padding: 10px 12px;
				background: #fafafa;
			}
			.guia-search-field input {
				flex: 1; border: none; background: none;
				font-size: 0.9rem; outline: none;
			}
			.guia-machine-list {
				position: absolute; top: 100%; left: 0; right: 0;
				background: #fff; border: 1px solid #eee; border-radius: 10px;
				box-shadow: 0 4px 16px rgba(0,0,0,0.1);
				z-index: 100; max-height: 200px; overflow-y: auto;
				margin-top: 4px;
			}
			.guia-machine-item {
				display: flex; align-items: center; gap: 0.6rem;
				padding: 0.6rem 0.8rem; cursor: pointer;
				transition: background 0.1s;
			}
			.guia-machine-item:hover { background: #fdf3ee; }
			.guia-machine-item img { width: 36px; height: 36px; object-fit: contain; border-radius: 6px; }
			.guia-machine-item span { font-size: 0.88rem; font-weight: 500; }
			.guia-machine-selected {
				display: flex; align-items: center; gap: 0.6rem;
				padding: 0.5rem 0.8rem; background: #fdf3ee;
				border-radius: 10px; margin-top: 0.4rem;
			}
			.guia-machine-selected img { border-radius: 6px; object-fit: contain; }
			.guia-machine-selected span { flex: 1; font-size: 0.88rem; font-weight: 600; color: #e05a00; }
			#guia-sel-clear { background: none; border: none; cursor: pointer; color: #999; font-size: 1rem; }

			.guia-upload-wrap { margin-bottom: 1rem; }
			.guia-upload-label {
				display: flex; align-items: center; gap: 0.6rem;
				padding: 12px 14px; border: 1.5px dashed #ddd; border-radius: 10px;
				cursor: pointer; transition: border-color 0.15s, background 0.15s;
				font-size: 0.88rem; color: #666;
			}
			.guia-upload-label:hover { border-color: #e05a00; background: #fdf3ee; color: #e05a00; }
			.guia-upload-label.has-file { border-color: #198754; background: #f0faf4; color: #198754; }

			.guia-submit-btn {
				width: 100%; padding: 13px; background: #e05a00; color: #fff;
				border: none; border-radius: 10px; font-weight: 700;
				font-size: 1rem; cursor: pointer; margin-top: 0.5rem;
				transition: opacity 0.2s;
			}
			.guia-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
			.guia-field { margin-bottom: 0.75rem; }
			.guia-field label { display: block; font-weight: 600; font-size: 0.83rem; margin-bottom: 4px; color: #444; }
			.guia-field input {
				width: 100%; padding: 9px 11px; border: 1.5px solid #ddd; border-radius: 8px;
				font-size: 0.88rem; box-sizing: border-box; outline: none;
			}
			.guia-field input:focus { border-color: #e05a00; }
			</style>

			<script>
			(function() {
				const API         = 'https://devapi.krear3d.com';
				const WP_USER_ID  = <?php echo (int) $gwa_user_id; ?>;
				const WP_EMAIL    = <?php echo json_encode( $gwa_user_email ); ?>;
				const WP_PHONE    = <?php echo json_encode( $gwa_user_phone ?: '' ); ?>;
				const WP_DNI      = <?php echo json_encode( $gwa_user_dni ?: '' ); ?>;

				const INTRANET     = 'https://devintranet.krear3d.com';
				const MACHINES_URL = `${INTRANET}/static/images/uploads/machines/`;

				let selectedMachine = null;
				let searchTimeout   = null;
				let cachedProfile   = null;

				// ── Cargar equipos aprobados ─────────────────────────────────────
				async function loadMyGuides() {
					try {
						const r = await fetch(`${API}/guide/my?wp_user_id=${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						renderGuideCards(j.data || []);
					} catch(e) {}
				}

				function renderGuideCards(guides) {
					const grid   = document.getElementById('guias-grid');
					const addBtn = document.getElementById('guia-add-btn');
					grid.querySelectorAll('.guia-card').forEach(el => el.remove());

					guides.forEach(g => {
						const isPending = g.status === 'pending';
						const card = document.createElement('div');
						card.className = 'guia-card' + (isPending ? ' guia-card-pending' : '');
						card.innerHTML = `
							${isPending ? '<div class="guia-badge-pending">Pendiente</div>' : ''}
							<img src="${MACHINES_URL}${g.machine_image}" alt="${g.machine_name}">
							<div class="guia-card-brand">${g.brand_name}</div>
							<div class="guia-card-name">${g.machine_name}</div>
						`;
						if (!isPending) {
							card.addEventListener('click', () => openGuideDetail(g));
						}
						grid.insertBefore(card, addBtn);
					});
				}

				// ── Detalle del equipo ───────────────────────────────────────────
				async function openGuideDetail(guide) {
					const grid   = document.getElementById('guias-grid');
					const detail = document.getElementById('guia-detail-wrap');

					document.getElementById('guia-detail-img').src   = `${MACHINES_URL}${guide.machine_image}`;
					document.getElementById('guia-detail-name').textContent  = guide.machine_name;
					document.getElementById('guia-detail-brand').textContent = guide.brand_name;
					document.getElementById('guia-detail-desc').textContent  = '';
					document.getElementById('guia-detail-items').innerHTML   = '<p style="opacity:0.4;font-size:0.85rem">Cargando contenido...</p>';

					grid.style.display   = 'none';
					detail.style.display = 'flex';

					try {
						const r = await fetch(`${API}/guide/content/${guide.machine_id}?wp_user_id=${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						renderGuideContent(j.data || {}, guide.machine_id);
					} catch(e) {
						document.getElementById('guia-detail-items').innerHTML = '<p style="opacity:0.4;font-size:0.85rem">Sin contenido disponible.</p>';
					}
				}

				function renderGuideContent(content, machine_id) {
					document.getElementById('guia-detail-desc').textContent = content.description || '';
					const container = document.getElementById('guia-detail-items');
					container.innerHTML = '';

					const items = content.items || [];
					if (!items.length) {
						container.innerHTML = '<p style="opacity:0.4;font-size:0.85rem">Sin contenido disponible aún.</p>';
						return;
					}

					items.forEach(item => {
						const card = document.createElement('div');
						card.className = 'guia-item-card';
						let inner = `<div class="guia-item-title">${item.title || ''}</div>`;

						if (item.type === 'image' && item.filename) {
							inner += `<img src="${API}/guide/media/${item.filename}?wp_user_id=${WP_USER_ID}&machine_id=${machine_id}" alt="${item.title}">`;
						} else if (item.type === 'video' && item.url) {
							inner += `<a href="${item.url}" target="_blank" rel="noopener" class="guia-item-link">
								<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
								Ver video
							</a>`;
						} else if (item.type === 'pdf' && item.filename) {
							inner += `<a href="${API}/guide/media/${item.filename}?wp_user_id=${WP_USER_ID}&machine_id=${machine_id}" target="_blank" rel="noopener" class="guia-item-link">
								<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
								Ver PDF
							</a>`;
						}
						card.innerHTML = inner;
						container.appendChild(card);
					});
				}

				// ── Perfil cacheado (phone/dni) ─────────────────────────────────
				async function fetchProfile() {
					if (cachedProfile !== null) return cachedProfile;
					try {
						const r = await fetch(`${API}/approval/wp_profile/${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						cachedProfile = j.data || {};
					} catch(e) {
						cachedProfile = {};
					}
					return cachedProfile;
				}

				// ── Modal de solicitud ──────────────────────────────────────────
				async function openRequestModal() {
					selectedMachine = null;
					document.getElementById('guia-machine-input').value = '';
					document.getElementById('guia-machine-list').style.display = 'none';
					document.getElementById('guia-machine-selected').style.display = 'none';
					document.getElementById('guia-voucher-input').value = '';
					document.getElementById('guia-upload-text').textContent = 'Adjuntar boleta / factura (PDF o imagen)';
					document.getElementById('guia-upload-label').classList.remove('has-file');
					document.getElementById('guia-request-error').style.display = 'none';

					// Mostrar campos de teléfono/DNI solo si no están disponibles
					const profile = await fetchProfile();
					const phone = profile.phone || WP_PHONE;
					const dni   = profile.dni   || WP_DNI;
					const profileFields = document.getElementById('guia-profile-fields');
					if (phone && dni) {
						profileFields.style.display = 'none';
					} else {
						profileFields.style.display = 'block';
						document.getElementById('guia-phone-input').value = phone || '';
						document.getElementById('guia-dni-input').value   = dni   || '';
					}

					document.getElementById('modal-guia-request').style.display = 'flex';
				}

				function closeRequestModal() {
					document.getElementById('modal-guia-request').style.display = 'none';
				}

				// ── Búsqueda de máquina ─────────────────────────────────────────
				async function searchMachines(q) {
					if (!q || q.length < 2) {
						document.getElementById('guia-machine-list').style.display = 'none';
						return;
					}
					try {
						const r = await fetch(`${API}/machine/find/${encodeURIComponent(q)}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						renderMachineList(j.data || []);
					} catch(e) {}
				}

				function renderMachineList(machines) {
					const list = document.getElementById('guia-machine-list');
					list.innerHTML = '';
					if (!machines.length) { list.style.display = 'none'; return; }

					machines.forEach(m => {
						const item = document.createElement('div');
						item.className = 'guia-machine-item';
						item.innerHTML = `
							<img src="${MACHINES_URL}${m.image}" alt="">
							<span>${m.name}</span>
						`;
						item.addEventListener('click', () => selectMachine(m));
						list.appendChild(item);
					});
					list.style.display = 'block';
				}

				function selectMachine(m) {
					selectedMachine = m;
					document.getElementById('guia-machine-list').style.display = 'none';
					document.getElementById('guia-machine-input').value = '';
					const sel = document.getElementById('guia-machine-selected');
					document.getElementById('guia-sel-img').src = `${MACHINES_URL}${m.image}`;
					document.getElementById('guia-sel-name').textContent = m.name;
					sel.style.display = 'flex';
				}

				// ── Submit solicitud ────────────────────────────────────────────
				async function submitRequest() {
					const errEl = document.getElementById('guia-request-error');
					errEl.style.display = 'none';

					if (!selectedMachine) {
						errEl.textContent = 'Selecciona el equipo.';
						errEl.style.display = 'block';
						return;
					}

					const voucher = document.getElementById('guia-voucher-input').files[0];
					if (!voucher) {
						errEl.textContent = 'Adjunta tu boleta o factura.';
						errEl.style.display = 'block';
						return;
					}

					// Obtener phone/dni: del perfil cacheado o de los campos del modal
					const profile = cachedProfile || {};
					let phone = profile.phone || WP_PHONE;
					let dni   = profile.dni   || WP_DNI;

					const profileFields = document.getElementById('guia-profile-fields');
					if (profileFields.style.display !== 'none') {
						phone = document.getElementById('guia-phone-input').value.trim();
						dni   = document.getElementById('guia-dni-input').value.trim();
						if (!phone || !dni) {
							errEl.textContent = 'Ingresa tu teléfono y DNI.';
							errEl.style.display = 'block';
							return;
						}
						if (!/^\d{8}$/.test(dni)) {
							errEl.textContent = 'El DNI debe tener 8 dígitos.';
							errEl.style.display = 'block';
							return;
						}
					}

					const btn = document.getElementById('guia-request-submit');
					btn.disabled = true;
					btn.textContent = 'Enviando...';

					const fd = new FormData();
					fd.append('wp_user_id',  WP_USER_ID);
					fd.append('machine_id',  selectedMachine.id);
					fd.append('email',       WP_EMAIL);
					fd.append('phone',       phone);
					fd.append('dni',         dni);
					fd.append('wp_username', '');
					fd.append('voucher',     voucher);

					try {
						const r = await fetch(`${API}/guide/request`, { method: 'POST', body: fd });
						const j = await r.json();
						if (j.success) {
							// Cachear para que futuras solicitudes no vuelvan a pedir datos
							cachedProfile = { phone, dni, email: WP_EMAIL };
							closeRequestModal();
							await loadMyGuides();
						} else {
							errEl.textContent = j.data?.message || 'Error al enviar la solicitud.';
							errEl.style.display = 'block';
						}
					} catch(e) {
						errEl.textContent = 'Error de conexión.';
						errEl.style.display = 'block';
					} finally {
						btn.disabled = false;
						btn.textContent = 'Enviar solicitud';
					}
				}

				// ── Eventos ─────────────────────────────────────────────────────
				document.addEventListener('DOMContentLoaded', function() {
					loadMyGuides();

					document.getElementById('guia-add-btn').addEventListener('click', openRequestModal);
					document.getElementById('modal-guia-close').addEventListener('click', closeRequestModal);
					document.getElementById('modal-guia-request').addEventListener('click', function(e) {
						if (e.target === this) closeRequestModal();
					});

					document.getElementById('guia-machine-input').addEventListener('input', function() {
						clearTimeout(searchTimeout);
						searchTimeout = setTimeout(() => searchMachines(this.value.trim()), 280);
					});

					document.getElementById('guia-sel-clear').addEventListener('click', function() {
						selectedMachine = null;
						document.getElementById('guia-machine-selected').style.display = 'none';
					});

					document.getElementById('guia-voucher-input').addEventListener('change', function() {
						const label = document.getElementById('guia-upload-label');
						const text  = document.getElementById('guia-upload-text');
						if (this.files[0]) {
							text.textContent = this.files[0].name;
							label.classList.add('has-file');
						} else {
							text.textContent = 'Adjuntar boleta / factura (PDF o imagen)';
							label.classList.remove('has-file');
						}
					});

					document.getElementById('guia-request-submit').addEventListener('click', submitRequest);

					document.getElementById('guia-back-btn').addEventListener('click', function() {
						document.getElementById('guia-detail-wrap').style.display = 'none';
						document.getElementById('guias-grid').style.display = 'flex';
					});
				});
			})();
			</script>
		  </div>
		  <!-- ═══════════ /GUÍAS ═══════════ -->

		  <div id="section-trueke" class="section-content"  style="display:none;">
		     <div class="procedimiento">
				<h1>¿CÓMO <span>FUNCIONA?</span></h1>
				<div class="cards">
				  <div>
					<div class="im">
					  <img
						src="/wp-content/uploads/2025/01/trueke-1.webp"
						alt=""
					  />
					</div>
					<p><span>Visítanos en</span><br />nuestra tienda en Miraflores</p>
				  </div>
				  <div>
					<div class="im">
					  <img
						src="/wp-content/uploads/2025/01/trueke-2.webp"
						alt=""
					  />
					</div>
					<p>
					  <span>Entrega tu Impresora 3D</span><br />antigua para una
					  evaluación
					</p>
				  </div>
				  <div>
					<div class="im">
					  <img
						src="/wp-content/uploads/2025/01/trueke-pago-2.webp"
						alt=""
					  />
					</div>
					<p><span>Te daremos el valor</span><br />como parte de pago</p>
				  </div>
				  <div>
					<div class="im">
					  <img
						src="/wp-content/uploads/2025/01/trueke-4.webp"
						alt=""
					  />
					</div>
					<p>
					  <span>Elige tu nueva Impresora 3D</span><br />disponible dentro
					  del plan
					</p>
				  </div>
				  <div>
					<div class="im">
					  <img
						src="/wp-content/uploads/2025/01/trueke-5.webp"
						alt=""
					  />
					</div>
					<p><span>¡Y Trueke listo!</span><br />Renueva tu Impresora 3D</p>
				  </div>
				</div>
			  </div>
			  <div class="ong">
				<img
				  src="/wp-content/uploads/2025/01/ban-dona.webp"
				  alt=""
				/>
				<div class="txts">
				  <img
					src="/wp-content/uploads/2025/01/logo-aca1.webp"
					alt=""
				  />
				  <p>Dona, Recicla y Ayuda</p>
				  <p>
					Al donar con nosotros, reduces residuos y extiendes la vida útil de
					los equipos, contribuyendo a cuidar el medio ambiente.
				  </p>
				  <p>
					Al mismo tiempo, tus donaciones apoyan a comunidades vulnerables,
					brindando ayuda real a quienes más lo necesitan.
				  </p>
				  <p>
					Las impresoras 3D que recaudamos serán entregadas a la ONG
					<span>A Caminar</span>, para brindar a niños y niñas en situación de
					pobreza la oportunidad de explorar y conocer el mundo 3D o por medio
					de su reciclaje se puede disminuir la contaminación de nuestro
					ecosistema y apoyar proyectos sociales.
				  </p>
				</div>
			  </div>
			  <div class="niveles">
				<h1>NIVELES DE <span>TRUEKE</span></h1>
				<p>
				  Conoce el rango de descuento que obtendrás por tu impresora 3D antigua
				  y después de la evaluación te daremos el valor final que te servirá
				  como parte de pago.
				</p>
				<div class="nivs">
				  <div class="niv">
					<p>NIVEL 1</p>
					<p>
					  Impresoras 3D en buenas condiciones, capaces de generar
					  impresiones 3D y con detalles de uso menores.
					</p>
					<p><span>DESCUENTO</span>S/300 - S/500</p>
				  </div>
				  <div class="niv">
					<p>NIVEL 2</p>
					<p>
					  Impresoras 3D funcionales, pero no producen impresiones de buena
					  calidad y requieren mantenimiento correctivo.
					</p>
					<p><span>DESCUENTO</span>S/100 - S/300</p>
				  </div>
				  <div class="niv">
					<p>NIVEL 3</p>
					<p>
					  Impresoras 3D con daños graves que impiden su funcionamiento y
					  cuya reparación supera el valor del equipo.
					</p>
					<p><span>DESCUENTO</span>S/10 - S/100</p>
				  </div>
				  <div class="niv">
					<p>NIVEL 4</p>
					<p>
					  Impresoras 3D en cualquier grado que quieras donar para proyectos
					  sociales a través de una ONG.
					</p>
					<p>DONACIÓN</p>
				  </div>
				</div>
			  </div>
			  <div class="redir">
				<a href="/trueke/">¡Únete a Trueke!</a>
			  </div>
		  </div>
			<div id="kd-wc-content">
			<?php do_action( 'woocommerce_account_content' ); ?>
			</div>
		</div>
    	</div>
	</div>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector("#kd-dashboard .dash .woocommerce-MyAccount-content #section-beneficios .levels .fases");

  if (!container) return;

  const fasItems = container.querySelectorAll(".imas .fase");
  const circles = container.querySelectorAll(".bar .circle");
  const lines = container.querySelectorAll(".bar .line");

  function activarNivel(index) {
    fasItems.forEach(fas => fas.classList.remove("active"));
    circles.forEach(circle => circle.classList.remove("active"));
    lines.forEach(line => line.classList.remove("active"));

    fasItems[index]?.classList.add("active");
    circles[index]?.classList.add("active");

    for (let i = 0; i < index; i++) {
      lines[i]?.classList.add("active");
    }
  }

  fasItems.forEach((fas, index) => {
    fas.addEventListener("click", () => {
      activarNivel(index);
    });
  });

  circles.forEach((circle, index) => {
    circle.addEventListener("click", () => {
      activarNivel(index);
    });
  });
});

</script>
