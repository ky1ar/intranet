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
header.custom { box-shadow: none; }

/* ═══════════════════════════════════════════════
   KD DASHBOARD — Krear Dashboard
═══════════════════════════════════════════════ */
#kd-dashboard {
	background: #ffffff;
	padding: 0.5rem;
	box-sizing: border-box;
}
#kd-dashboard .ttl-user { display: none; }
#kd-dashboard .wrapper  { max-width: 1200px; margin: 0 auto; }
#kd-dashboard .dash {
	display: grid;
	grid-template-columns: 260px 1fr;
	gap: 1.25rem;
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
    background: #f2f2f2;
    border-radius: 1.5rem;
    padding: 1.5rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
	position: relative;
    overflow: hidden;
}
.kd-deco {
    position: absolute;
    top: 0;
    right: 0;
    pointer-events: none; /* no interfiere con clicks */
    z-index: 0;
}

/* asegurá que el contenido quede por encima del decorado */
.kd-avatar-wrap,
.kd-name,
.kd-username {
    position: relative;
    z-index: 1;
}
.kd-avatar-wrap {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
    padding: 0.4rem;
}
.kd-avatar-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	border-radius: 100%;
}
.kd-avatar-default { padding: 12px; }
.kd-name {
    font-weight: 700;
    font-size: 1rem;
    margin: 0;
    color: var(--secondary);
}
.kd-username {
    font-size: 0.8rem;
    opacity: 0.5;
    margin: 0;
    margin-top: -0.85rem;
    line-height: 0.85rem;
    font-weight: 500;
}

/* ── Nav Card ── */
.kd-nav-card {
    background: #f2f2f2;
    border-radius: 1.5rem;
    padding: 1.5rem 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
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
	min-height: 500px;
	width: 100% !important;
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
				<h2>Servicios Exclusivos</h2>
				<p>Accede a nuestros servicios especiales para clientes Krear 3D.</p>
			</div>
			<div class="servicios-cards">

				<div class="servicio-card" data-type="stl">
					<div class="servicio-icon">
						<img src="/wp-content/uploads/2025/07/cuenta.png" alt="STL" class="servicio-img-icon">
					</div>
					<h3>STL</h3>
					<p class="servicio-desc">Accede a nuestra biblioteca de archivos STL exclusivos para impresión 3D.</p>
					<div class="servicio-action">
						<span class="servicio-status-badge" style="display:none;"></span>
						<button class="btn-solicitar" data-type="stl">Solicitar acceso</button>
						<a class="btn-acceder" data-type="stl" href="#" target="_blank" style="display:none;">Acceder</a>
					</div>
				</div>

				<div class="servicio-card" data-type="cursos">
					<div class="servicio-icon">
						<img src="/wp-content/uploads/2025/07/cuenta.png" alt="Cursos" class="servicio-img-icon">
					</div>
					<h3>Cursos</h3>
					<p class="servicio-desc">Accede a cursos especializados en impresión 3D, diseño y más.</p>
					<div class="servicio-action">
						<span class="servicio-status-badge" style="display:none;"></span>
						<button class="btn-solicitar" data-type="cursos">Solicitar acceso</button>
						<a class="btn-acceder" data-type="cursos" href="#" target="_blank" style="display:none;">Acceder</a>
					</div>
				</div>

			</div>

			<!-- Modal: datos de perfil faltantes -->
			<div id="modal-perfil-servicio" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
				<div style="background:#fff; border-radius:12px; padding:2rem; max-width:400px; width:90%; position:relative;">
					<button id="modal-perfil-close" style="position:absolute; top:1rem; right:1rem; background:none; border:none; font-size:1.4rem; cursor:pointer;">&times;</button>
					<h3 style="margin-bottom:0.5rem;">Completa tus datos</h3>
					<p style="margin-bottom:1.2rem; color:#666; font-size:0.9rem;">Necesitamos tu teléfono y DNI para procesar tu solicitud. Solo te lo pediremos esta vez.</p>
					<input type="hidden" id="modal-servicio-type" value="">
					<div style="margin-bottom:1rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">Teléfono</label>
						<input type="tel" id="input-phone" placeholder="Ej: 987654321" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
					</div>
					<div style="margin-bottom:1.5rem;">
						<label style="font-weight:600; display:block; margin-bottom:4px;">DNI</label>
						<input type="text" id="input-dni" placeholder="Ej: 12345678" maxlength="8" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box;">
					</div>
					<button id="modal-perfil-submit" style="width:100%; padding:12px; background:#e05a00; color:#fff; border:none; border-radius:8px; font-weight:700; font-size:1rem; cursor:pointer;">Enviar solicitud</button>
					<p id="modal-perfil-error" style="color:red; margin-top:0.7rem; display:none;"></p>
				</div>
			</div>

			<style>
			.servicios-section { flex-direction: column; gap: 1.5rem; padding: 1.5rem; }
			.servicios-header h2 { margin: 0 0 0.3rem; font-size: 1.4rem; }
			.servicios-header p { color: #666; margin: 0; }
			.servicios-cards { display: flex; flex-wrap: wrap; gap: 1.5rem; }
			.servicio-card {
				background: #fff;
				border: 1px solid #eee;
				border-radius: 12px;
				padding: 1.5rem;
				flex: 1 1 220px;
				max-width: 280px;
				display: flex;
				flex-direction: column;
				gap: 0.8rem;
				box-shadow: 0 2px 8px rgba(0,0,0,0.06);
			}
			.servicio-card h3 { margin: 0; font-size: 1.1rem; }
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
			</style>

			<script>
			(function() {
				const API = 'https://devapi.krear3d.com';
				const WP_USER_ID   = <?php echo (int) $wp_user_id; ?>;
				const WP_EMAIL     = <?php echo json_encode( $wp_user_email ); ?>;
				const WP_USERNAME  = <?php echo json_encode( $wp_user_display ); ?>;
				const WP_PHONE     = <?php echo json_encode( $wp_user_phone ?: '' ); ?>;
				const WP_DNI       = <?php echo json_encode( $wp_user_dni ?: '' ); ?>;

				let cachedProfile = null;

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

				async function checkStatuses() {
					const types = ['stl', 'cursos'];
					for (const type of types) {
						try {
							const r = await fetch(`${API}/approval/status?wp_user_id=${WP_USER_ID}&type=${type}`, { headers: { 'X-No-Toast': '1' } });
							const j = await r.json();
							const data = j.data || {};
							applyStatus(type, data);
						} catch(e) {}
					}
				}

				function applyStatus(type, data) {
					const card = document.querySelector(`.servicio-card[data-type="${type}"]`);
					if (!card) return;
					const badge    = card.querySelector('.servicio-status-badge');
					const btnSolic = card.querySelector('.btn-solicitar');
					const btnAcc   = card.querySelector('.btn-acceder');

					if (data.status === 'approved') {
						btnSolic.style.display = 'none';
						badge.style.display    = 'inline-block';
						badge.className        = 'servicio-status-badge badge-approved';
						badge.textContent      = 'Aprobado';
						if (data.access_url) {
							btnAcc.href          = data.access_url;
							btnAcc.style.display = 'inline-block';
						}
					} else if (data.status === 'pending') {
						btnSolic.disabled      = true;
						btnSolic.textContent   = 'Solicitud enviada';
						badge.style.display    = 'inline-block';
						badge.className        = 'servicio-status-badge badge-pending';
						badge.textContent      = 'En revisión';
					} else if (data.status === 'rejected') {
						badge.style.display    = 'inline-block';
						badge.className        = 'servicio-status-badge badge-rejected';
						badge.textContent      = 'Rechazado';
					}
				}

				async function submitRequest(type, phone, dni) {
					const body = {
						wp_user_id:  WP_USER_ID,
						type_slug:   type,
						email:       WP_EMAIL,
						phone:       phone,
						dni:         dni,
						wp_username: WP_USERNAME,
					};
					const r = await fetch(`${API}/approval/request`, {
						method:  'POST',
						headers: { 'Content-Type': 'application/json' },
						body:    JSON.stringify(body),
					});
					return r.json();
				}

				async function handleSolicitar(type) {
					const profile = await fetchProfile();
					const phone = profile.phone || WP_PHONE;
					const dni   = profile.dni   || WP_DNI;

					if (phone && dni) {
						await doSubmit(type, phone, dni);
					} else {
						openModal(type, phone, dni);
					}
				}

				async function doSubmit(type, phone, dni) {
					if (!phone || !dni) return;
					if (!WP_EMAIL) { alert('No se encontró tu correo electrónico.'); return; }
					cachedProfile = { phone, dni, email: WP_EMAIL };
					const j = await submitRequest(type, phone, dni);
					closeModal();
					await checkStatuses();
				}

				function openModal(type, existingPhone, existingDni) {
					document.getElementById('modal-servicio-type').value = type;
					document.getElementById('input-phone').value = existingPhone || '';
					document.getElementById('input-dni').value   = existingDni   || '';
					document.getElementById('modal-perfil-error').style.display = 'none';
					const modal = document.getElementById('modal-perfil-servicio');
					modal.style.display = 'flex';
				}

				function closeModal() {
					document.getElementById('modal-perfil-servicio').style.display = 'none';
				}

				document.addEventListener('DOMContentLoaded', function() {
					checkStatuses();

					document.querySelectorAll('.btn-solicitar').forEach(btn => {
						btn.addEventListener('click', () => handleSolicitar(btn.dataset.type));
					});

					document.getElementById('modal-perfil-close').addEventListener('click', closeModal);

					document.getElementById('modal-perfil-submit').addEventListener('click', async function() {
						const type  = document.getElementById('modal-servicio-type').value;
						const phone = document.getElementById('input-phone').value.trim();
						const dni   = document.getElementById('input-dni').value.trim();
						const errEl = document.getElementById('modal-perfil-error');

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
						errEl.style.display = 'none';
						this.disabled = true;
						this.textContent = 'Enviando...';
						await doSubmit(type, phone, dni);
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
