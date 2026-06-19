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

$kd_is_orders  = is_wc_endpoint_url('orders') || is_wc_endpoint_url('view-order');
$kd_is_address = is_wc_endpoint_url('edit-address');
$kd_is_account = is_wc_endpoint_url('edit-account');
$kd_is_wc      = $kd_is_orders || $kd_is_address || $kd_is_account;
$kd_default    = ! $kd_is_wc; // landing /mi-cuenta/ => Beneficios (seccion servicios)
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
    border-radius: 1rem;
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
.kd-item-salir {
	color: #999;
    padding-top: 1rem;
    border-top: 1px solid #f5f5f5;
}
.kd-item-salir:hover {
	color: #c0392b;
    opacity: 1;
}

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
	border-radius: 1rem;
	box-shadow: 0 2px 12px rgba(0,0,0,0.06);
	padding: 2rem;
	/* min-height: 500px; */
	width: 100% !important;
}

/* ═══ Editar perfil ═══ */
#kd-wc-content .k3d-cards-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1.5rem;
	align-items: start;
}
#kd-wc-content .k3d-cards-grid .k3d-card { margin-bottom: 0; }
#kd-wc-content .k3d-edit-profile {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1.1rem 1rem;
	align-items: start;
}
/* Nombre | Apellidos · Nombre visible | Imagen · Correo (ancho completo) */
#kd-wc-content .k3d-edit-profile .k3d-row-email { grid-column: 1 / -1; }
#kd-wc-content .k3d-edit-profile .edit-photo {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	align-self: start;
	gap: 0.6rem;
	min-width: 0;
}

/* Filas y labels */
#kd-wc-content .woocommerce-EditAccountForm .form-row {
	padding: 0;
	margin: 0;
	display: flex;
	flex-direction: column;
	width: 100%;
}
#kd-wc-content .woocommerce-EditAccountForm .form-row br {
	display: none;
}
#kd-wc-content .woocommerce-EditAccountForm label {
	opacity: 0.55;
	font-weight: 500;
	font-size: 0.8rem;
	margin: 0;
}
#kd-wc-content .woocommerce-EditAccountForm .form-row span em {
	opacity: 0.5;
    font-size: 0.6rem;
    font-style: italic;
    font-weight: 400;
    line-height: 0.7rem;
    display: none;
    margin-top: 0.25rem;
}

/* Inputs (texto, email, contraseña, select) */
#kd-wc-content .woocommerce-EditAccountForm .input-text,
#kd-wc-content .woocommerce-EditAccountForm input[type="text"],
#kd-wc-content .woocommerce-EditAccountForm input[type="email"],
#kd-wc-content .woocommerce-EditAccountForm input[type="tel"],
#kd-wc-content .woocommerce-EditAccountForm input[type="password"],
#kd-wc-content .woocommerce-EditAccountForm select {
	width: 100%;
	box-sizing: border-box;
	font-family: inherit;
	font-weight: 500;
	font-size: 0.9rem;
	color: #2b2b2b;
	border: 1px solid #e2e2e2;
	border-radius: 0.75rem;
	padding: 0.85rem 1rem;
	background: #fff;
	outline: none;
	transition: border-color .15s, box-shadow .15s;
}
#kd-wc-content .woocommerce-EditAccountForm .input-text:focus,
#kd-wc-content .woocommerce-EditAccountForm input:focus,
#kd-wc-content .woocommerce-EditAccountForm select:focus {
	border-color: var(--primary, #e05a00);
	box-shadow: 0 0 0 3px var(--primaryopacity, #fdeee4);
}

/* Tarjeta de contraseña: filas full-width y espaciadas */
#kd-wc-content .woocommerce-EditAccountForm fieldset .form-row { margin-bottom: 1.1rem; }
#kd-wc-content .woocommerce-EditAccountForm fieldset .form-row:last-child { margin-bottom: 0; }

/* Imagen de perfil */
#kd-wc-content .edit-photo label { width: 100%; opacity: 0.55; font-weight: 500; font-size: 0.8rem; }
#kd-wc-content .edit-photo img {
	width: 5rem;
	height: 5rem;
	min-width: 5rem;
	aspect-ratio: 1 / 1;
	object-fit: cover;
	border-radius: 0.85rem;
	border: 1px solid #eee;
	display: none !important;
}
#kd-wc-content .edit-photo input[type="file"] {
	display: block;
	width: 100%;
	max-width: 100%;
	height: auto;
	flex: none;
	font-family: inherit;
	font-size: 0.78rem;
	color: #888;
	border: 1px dashed #d8d8d8;
	border-radius: 0.75rem;
	padding: 0.4rem;
	box-sizing: border-box;
	background: #fafafa;
	cursor: pointer;
}
#kd-wc-content .edit-photo input[type="file"]::file-selector-button,
#kd-wc-content .edit-photo input[type="file"]::-webkit-file-upload-button {
	font-family: inherit;
	font-weight: 600;
	font-size: 0.78rem;
	color: #fff;
	background: var(--primary, #e05a00);
	border: none;
	border-radius: 0.5rem;
	padding: 0.5rem 0.85rem;
	margin-right: 0.6rem;
	cursor: pointer;
	transition: opacity .2s;
}
#kd-wc-content .edit-photo input[type="file"]::file-selector-button:hover { opacity: 0.85; }

@media (max-width: 1024px) {
	#kd-wc-content .k3d-cards-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
	#kd-wc-content .k3d-edit-profile { grid-template-columns: 1fr; }
}

/* ── Loader AJAX ── */
#kd-wc-content { position: relative; min-height: 120px; }
.kd-loading {
	position: absolute; inset: 0;
	display: flex; align-items: center; justify-content: center;
	background: rgba(255,255,255,0.6); border-radius: 16px; z-index: 5;
}
.kd-spinner {
	width: 28px; height: 28px; border-radius: 50%;
	border: 3px solid #e9e9e9; border-top-color: var(--primary, #e05a00);
	animation: kd-spin .7s linear infinite;
}
@keyframes kd-spin { to { transform: rotate(360deg); } }

/* ── Tarjetas de Perfil (Informacion / Contrasena) ── */
.woocommerce-EditAccountForm .k3d-card {
	border: 1px solid #00000012;
	border-radius: 1rem;
	padding: 1.75rem;
	margin-bottom: 1.5rem;
}
.woocommerce-EditAccountForm .k3d-card:last-of-type { margin-bottom: 0; }
.woocommerce-EditAccountForm .k3d-card-head { margin-bottom: 1rem; }
.woocommerce-EditAccountForm .k3d-card-head h3 {
	margin: 0;
	font-size: 1.1rem;
	font-weight: 700;
	color: var(--secondary, #1f2937);
	text-transform: none;
}
.woocommerce-EditAccountForm .k3d-card-head p {
	margin: -0.1rem 0 0;
	font-size: 0.8rem;
	opacity: 0.5;
}
.woocommerce-EditAccountForm fieldset { display: block; border: none; padding: 0; margin: 0; }
.woocommerce-EditAccountForm fieldset legend { display: none; }
.woocommerce-EditAccountForm .k3d-actions { margin: 1.25rem 0 0; }
/* ── Botones (Perfil / Direcciones / Pedido) ── */
#kd-wc-content .button,
#kd-wc-content .woocommerce-Button,
#kd-wc-content button[type="submit"] {
	margin: 0;
	background-color: var(--primary, #e05a00);
	color: var(--white, #fff);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	min-height: 2.75rem;
	border-radius: 2rem;
	padding: 0 1.5rem;
	font-size: 0.8rem;
	font-family: inherit;
	font-weight: 600;
	border: none;
	cursor: pointer;
	user-select: none;
	text-decoration: none;
	transition: opacity 0.3s ease;
}
#kd-wc-content .button:hover,
#kd-wc-content .woocommerce-Button:hover,
#kd-wc-content button[type="submit"]:hover { opacity: 0.85; }
#kd-wc-content .woocommerce-EditAccountForm .k3d-actions { display: flex; margin: 1.25rem 0 0; }
#kd-wc-content .woocommerce-EditAccountForm .k3d-actions .button { display: flex; width: 100%; align-self: stretch; }

/* ── Lista de pedidos ── */
#section-pedidos { flex-direction: column; gap: 1.25rem; align-items: stretch; }
#section-pedidos .kd-orders-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
#section-pedidos .kd-orders-head h2 { margin: 0; font-size: 1.25rem; font-weight: 800; }
.kd-orders-filter {
	display: inline-flex; align-items: center; gap: 0.5rem;
	border: 1px solid #e4e4e4; border-radius: 0.75rem; padding: 0.5rem 0.85rem; background: #fff;
}
.kd-orders-filter svg { width: 1rem; height: 1rem; opacity: 0.5; }
.kd-orders-filter select {
	border: none; background: none; font-family: inherit; font-size: 0.85rem;
	font-weight: 600; color: #444; outline: none; cursor: pointer;
}
.kd-orders-list { display: flex; flex-direction: column; gap: 0.85rem; }
.kd-order-card {
	display: flex; align-items: center; gap: 1.25rem;
	padding: 1rem 1.5rem; border: 1px solid #00000010; border-radius: 1rem;
	background: #fff; text-decoration: none; color: inherit;
	transition: box-shadow .15s, transform .1s;
}
.kd-order-card:hover { box-shadow: 0 6px 18px rgba(0,0,0,.07); }
.kd-order-card:active { transform: scale(.997); }
.kd-order-ico {
	width: 3rem; height: 3rem; min-width: 3rem; border-radius: 50%;
	background: var(--primaryopacity, #fdeee4); color: var(--primary, #e05a00);
	display: flex; align-items: center; justify-content: center;
}
.kd-order-ico svg { width: 1.4rem; height: 1.4rem; }
.kd-order-main { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; min-width: 0; }
.kd-order-num { font-weight: 700; font-size: 0.95rem; color: #222; }
.kd-order-date { font-size: 0.78rem; color: #9aa0a6; }
.kd-order-status {
	display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.4rem 0.85rem;
    border-radius: 2rem;
    white-space: nowrap;
    min-width: 9rem;
    justify-content: center;
}
.kd-order-status svg { width: 1rem; height: 1rem; flex-shrink: 0; }
.kd-order-totals { display: flex; flex-direction: column; align-items: flex-end; gap: 0.1rem; min-width: 5rem; }
.kd-order-total-lbl { font-size: 0.72rem; color: #9aa0a6; }
.kd-order-total {
	font-weight: 700;
	font-size: 0.95rem;
	color: var(--primary, #e05a00);
	white-space: nowrap;
	display: flex;
    flex-direction: column;
}
.kd-order-total del {
    opacity: 0.5;
    font-weight: 500;
    color: #999;
    font-size: 0.8rem;
    text-align: right;
}
.kd-order-total ins { text-decoration: none; text-align: right; }
.kd-order-chev { color: #c9c9c9; flex-shrink: 0; display: flex; }
.kd-order-chev svg { width: 1.1rem; height: 1.1rem; }
.kd-orders-empty { opacity: 0.5; }
.kd-st-completed { background: #e6f4ea; color: #1e7e44; }
.kd-st-processing, .kd-st-refunded { background: #e8f0fe; color: #1a56c4; }
.kd-st-hold { background: #fff3e0; color: #b25b00; }
.kd-st-cancelled { background: #fdecec; color: #c0392b; }
@media (max-width: 680px) {
	.kd-order-card { flex-wrap: wrap; }
	.kd-order-status { order: 4; }
	.kd-order-totals { order: 3; margin-left: auto; }
	.kd-order-chev { display: none; }
}

/* ═══ Vista de pedido (view-order) ═══ */
#kd-wc-content .kd-order-view { display: flex; flex-direction: column; gap: 1.25rem; }
#kd-wc-content .kd-ov-head {
	display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}
#kd-wc-content .kd-ov-head-l { display: flex; align-items: center; gap: 1rem; }
#kd-wc-content .kd-ov-ico {
	width: 3rem; height: 3rem; min-width: 3rem; border-radius: 50%;
	background: var(--primaryopacity, #fdeee4); color: var(--primary, #e05a00);
	display: flex; align-items: center; justify-content: center;
}
#kd-wc-content .kd-ov-ico svg { width: 1.4rem; height: 1.4rem; }
#kd-wc-content .kd-ov-head h2 { margin: 0; font-size: 1.25rem; font-weight: 800; }
#kd-wc-content .kd-ov-date { font-size: 0.8rem; color: #9aa0a6; }
#kd-wc-content .kd-ov-pay { align-self: flex-start; }
#kd-wc-content .kd-ov-card {
	background: #fff; border: 1px solid #eee; border-radius: 14px;
	padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
#kd-wc-content .kd-ov-card-title {
	font-size: 0.78rem; font-weight: 800; text-transform: uppercase;
	color: #9aa0a6; letter-spacing: 0.03em; margin-bottom: 1rem;
}
#kd-wc-content .kd-ov-items { display: flex; flex-direction: column; }
#kd-wc-content .kd-ov-item {
	display: flex; align-items: center; gap: 1rem;
	padding: 0.85rem 0; border-bottom: 1px solid #f2f2f2;
}
#kd-wc-content .kd-ov-item:first-child { padding-top: 0; }
#kd-wc-content .kd-ov-item-img {
	width: 3.25rem; height: 3.25rem; min-width: 3.25rem;
	border-radius: 0.6rem; overflow: hidden; background: #f7f7f7;
	display: flex; align-items: center; justify-content: center;
}
#kd-wc-content .kd-ov-item-img img { width: 100%; height: 100%; object-fit: cover; }
#kd-wc-content .kd-ov-item-info { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; min-width: 0; }
#kd-wc-content .kd-ov-item-name { font-weight: 600; font-size: 0.9rem; color: #222; }
#kd-wc-content .kd-ov-item-name a { color: inherit; text-decoration: none; }
#kd-wc-content .kd-ov-item-name a:hover { color: var(--primary, #e05a00); }
#kd-wc-content .kd-ov-item-qty { font-size: 0.78rem; color: #9aa0a6; }
#kd-wc-content .kd-ov-item-total { font-weight: 700; font-size: 0.9rem; white-space: nowrap; }
#kd-wc-content .kd-ov-totals {
	margin-top: 1rem; padding-top: 1rem; border-top: 2px solid #f2f2f2;
	display: flex; flex-direction: column; gap: 0.5rem;
}
#kd-wc-content .kd-ov-total-row { display: flex; justify-content: space-between; font-size: 0.88rem; color: #666; }
#kd-wc-content .kd-ov-total-row span:last-child { font-weight: 600; color: #333; }
#kd-wc-content .kd-ov-total-row.is-total {
	font-size: 1.05rem; font-weight: 800; padding-top: 0.6rem; margin-top: 0.2rem; border-top: 1px solid #f2f2f2;
}
#kd-wc-content .kd-ov-total-row.is-total span { color: var(--primary, #e05a00); font-weight: 800; }
#kd-wc-content .kd-ov-note { margin: 0; font-size: 0.9rem; color: #555; line-height: 1.6; }
#kd-wc-content .kd-ov-addresses { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; }
#kd-wc-content .kd-ov-card address { font-style: normal; line-height: 1.7; font-size: 0.88rem; color: #555; }
#kd-wc-content .kd-ov-contact { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #555; margin: 0.6rem 0 0; }
#kd-wc-content .kd-ov-contact svg { width: 0.95rem; height: 0.95rem; opacity: 0.5; flex-shrink: 0; }

/* ═══ Direcciones dentro del pedido (customer-details) ═══ */
#kd-wc-content .woocommerce-columns--addresses {
	display: flex;
	flex-wrap: wrap;
	gap: 1.25rem;
	margin: 0;
	width: 100%;
}
#kd-wc-content address {
	font-style: normal;
	line-height: 1.7;
	font-size: 0.85rem;
	color: #555;
}

/* ═══ Página de Direcciones (tarjetas estilo referencia) ═══ */
#kd-wc-content .kd-addr-intro { margin: 0 0 1.5rem; color: #555; font-size: 0.95rem; }
#kd-wc-content .kd-addr-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
	gap: 1.5rem;
	margin: 0;
}
#kd-wc-content .kd-addr-card {
	background: #fff;
	border: 1px solid #eee;
	border-radius: 16px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
	display: flex;
	flex-direction: column;
}
#kd-wc-content .kd-addr-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 1rem;
	padding: 1.5rem;
	border-bottom: 1px solid #f0f0f0;
	background: transparent;
}
#kd-wc-content .kd-addr-head-title { display: flex; align-items: center; gap: 0.9rem; }
#kd-wc-content .kd-addr-head-ico {
	width: 2.75rem; height: 2.75rem; min-width: 2.75rem;
	border-radius: 50%;
	background: var(--primaryopacity, #fdeee4);
	color: var(--primary, #e05a00);
	display: flex; align-items: center; justify-content: center;
}
#kd-wc-content .kd-addr-head-ico svg { width: 1.35rem; height: 1.35rem; }
#kd-wc-content .kd-addr-head h3 {
	margin: 0; font-size: 1rem; font-weight: 800; line-height: 1.2;
	text-transform: uppercase; color: var(--secondary, #1f2937);
}
#kd-wc-content .kd-addr-edit {
	display: inline-flex; align-items: center; gap: 0.4rem;
	font-size: 0.8rem; font-weight: 700;
	color: var(--primary, #e05a00); text-decoration: none;
	border: 1px solid var(--primary, #e05a00);
	padding: 0.5rem 1rem; border-radius: 2rem;
	transition: background 0.2s, color 0.2s; white-space: nowrap;
}
#kd-wc-content .kd-addr-edit svg { width: 0.9rem; height: 0.9rem; }
#kd-wc-content .kd-addr-edit:hover { background: var(--primary, #e05a00); color: #fff; }
#kd-wc-content .kd-addr-rows { padding: 0.5rem 1.5rem; }
#kd-wc-content .kd-addr-row {
	display: flex; align-items: center; gap: 1rem;
	padding: 1rem 0; border-bottom: 1px solid #f4f4f4;
}
#kd-wc-content .kd-addr-row:last-child { border-bottom: none; }
#kd-wc-content .kd-addr-row-ico {
	width: 2.5rem; height: 2.5rem; min-width: 2.5rem;
	border-radius: 50%;
	background: var(--primaryopacity, #fdeee4);
	color: var(--primary, #e05a00);
	display: flex; align-items: center; justify-content: center;
}
#kd-wc-content .kd-addr-row-ico svg { width: 1.15rem; height: 1.15rem; }
#kd-wc-content .kd-addr-row-data { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
#kd-wc-content .kd-addr-row-lbl { font-size: 0.78rem; color: #9aa0a6; }
#kd-wc-content .kd-addr-row-val { font-size: 0.95rem; font-weight: 600; color: #2b2b2b; word-break: break-word; }
#kd-wc-content .kd-addr-badge {
	display: flex; align-items: center; justify-content: center; gap: 0.5rem;
	margin: 0.5rem 1.5rem 1.5rem; padding: 0.85rem 1rem;
	border-radius: 0.85rem; font-size: 0.85rem; font-weight: 600;
	background: #ffeee4;
    color: var(--primary);
}
#kd-wc-content .kd-addr-badge svg { width: 1.1rem; height: 1.1rem; flex-shrink: 0; }
#kd-wc-content .kd-addr-empty { padding: 1.5rem; text-align: center; }
#kd-wc-content .kd-addr-empty p { color: #888; font-size: 0.88rem; margin: 0 0 1rem; }
#kd-wc-content .kd-addr-empty-btn {
	display: inline-flex; background: var(--primary, #e05a00); color: #fff;
	padding: 0.6rem 1.25rem; border-radius: 2rem; text-decoration: none;
	font-size: 0.8rem; font-weight: 600;
}

/* Formulario de direccion (al editar) */
#kd-wc-content .woocommerce-address-fields .form-row { margin: 0 0 0.6rem; }
#kd-wc-content .woocommerce-address-fields .form-row label {
	font-size: 0.8rem; font-weight: 500; opacity: 0.6; display: block; margin-bottom: 0.2rem;
}
#kd-wc-content .woocommerce-address-fields .input-text,
#kd-wc-content .woocommerce-address-fields select,
#kd-wc-content .woocommerce-address-fields .select2-selection {
	border: 1px solid #00000024;
	border-radius: 0.75rem;
	padding: 0.85rem 1rem;
	font-family: inherit;
	font-size: 0.85rem;
	width: 100%;
	box-sizing: border-box;
}
.woocommerce-account footer .activ {
	background-color: var(--gray) !important;
}
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
		  
			<div id="section-servicios" class="section-content servicios-section" style="display:<?php echo $kd_default ? 'flex' : 'none'; ?>;">
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

				<div class="servicio-card" data-type="stl" data-access-label="Acceder a K3D FAB" data-platform-url="https://stlkrear3d.com/">
					<div class="top">
						<div class="data">
							<span>Biblioteca</span>
							<div class="title">Modelos STL</div>
							<div class="type">K3D FAB</div>
							<p>Accede a nuestra biblioteca de archivos STL exclusivos para impresión 3D.</p>
							<ul>
								<li><b></b>Modelos listos para imprimir</li>
								<li><b></b>Descargas exclusivas</li>
								<li><b></b>Nuevos archivos cada mes</li></ul>
						</div>

						<div class="image">
							<img src="https://www.tiendakrear3d.com/wp-content/uploads/2026/06/stl.webp">
						</div>
					</div>

					<div class="bottom">
						<div class="icon">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"><path fill="#ea7134" d="M256 0 32 112v288l224 112 224-112V112L256 0zm0 53.3 158.7 79.4L256 212 97.3 132.7 256 53.3zM74.7 169.4 234.7 249v201.3L74.7 370.6V169.4zm202.6 280.9V249l160-79.6v201.2l-160 79.7z"/></svg>
						</div>
						<p>Ideal para makers que quieren empezar a imprimir al instante.</p>
						<div class="action">Acceder a K3D FAB</div>
					</div>
				</div>

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
			.servicios-cards {
				display: grid;
				gap: 1.5rem;
				grid-template-columns: 1fr 1fr;
			}
			
			.servicio-card {
				background: #fff;
				border: 1px solid #eee;
				border-radius: 12px;
				padding: 1.5rem;
				flex: 1 1 220px;
				flex-direction: column;
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
				border-radius: 0.35rem;
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
				padding: 0.75rem;
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
				padding: 0.5rem 1.25rem;
				border-radius: 1.5rem;
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
			.servicio-card .bottom .action.is-rejected { background-color: var(--secondary); cursor: default; }
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

                const TYPES = ['curso-fdm', 'curso-lcd', 'stl'];
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
                    // Si la tarjeta declara su propia URL (p.ej. STL), esa manda sobre
                    // lo que devuelva el API (que puede traer un access_url antiguo guardado).
                    card.dataset.accessUrl = card.dataset.platformUrl || data.access_url || PLATFORM;

                    action.classList.remove('is-pending', 'is-rejected');
                    if (status === 'approved') {
                        action.textContent = card.dataset.accessLabel || 'Acceder al curso';
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
                        window.open(card.dataset.accessUrl || card.dataset.platformUrl || PLATFORM, '_blank');
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

                    document.querySelectorAll('.servicio-card[data-type]').forEach(card => {
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
				<h2>Mis Manuales</h2>
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
					<img id="guia-detail-img" class="guia-detail-machine" src="" alt="">
					<div class="guia-detail-meta">
						<span class="guia-detail-eyebrow">Manual de equipo</span>
						<div class="guia-detail-name" id="guia-detail-name"></div>
						<div class="guia-detail-brand" id="guia-detail-brand"></div>
					</div>
					<img id="guia-detail-brand-img" class="guia-detail-brandlogo" src="" alt="">
				</div>
				<div class="guia-voltage-warning" role="alert">
					<span class="guia-voltage-ico">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
					</span>
					<div class="guia-voltage-text">
						<span class="guia-voltage-title">¡Importante! Selecciona siempre <strong>220V</strong></span>
						<span class="guia-voltage-sub">Antes de encender tu equipo, verifica que el selector de voltaje esté en <strong>220V</strong>. Usar 110V puede dañar la máquina.</span>
					</div>
				</div>
				<div class="guia-detail-desc" id="guia-detail-desc"></div>
				<div class="guia-detail-items" id="guia-detail-items"></div>
			</div>

			<!-- Modal: solicitar guía -->
			<div id="modal-guia-request" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
				<div class="guia-modal-inner">
					<button id="modal-guia-close" class="guia-modal-close">&times;</button>
					<h3>Solicitar manual de equipo</h3>
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

					<!-- N° de boleta / factura -->
					<div class="guia-field" style="margin-bottom:1rem;">
						<label>N° de boleta / factura</label>
						<input type="text" id="guia-invoice-input" placeholder="Ej: B001-12345">
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
			.guias-section { flex-direction: column; gap: 1.5rem; }
			.guias-header h2 { margin: 0 0 0.3rem; font-size: 1.4rem; }
			.guias-header p  { color: #666; margin: 0; }

			.guias-grid {
				display: grid;
				gap: 1rem;
				grid-template-columns: repeat(auto-fill, 12.5rem);
				background-color: var(--gray);
				padding: 1.5rem;
				border-radius: 1rem;
				margin: -0.5rem;
			}
			.guia-card {
				background: var(--white);
				border-radius: 0.75rem;
				padding: 1.25rem;
				display: flex;
				flex-direction: column;
				align-items: center;
				gap: 1.25rem;
				cursor: pointer;
				transition: var(--transition);
				position: relative;
			}
			.guia-card .guia-card-brand-img {
				width: 5.5rem;
				position: absolute;
				left: 1rem;
				top: 1.15rem;
				transition: var(--transition);
    			filter: grayscale(1);
			}
			.guia-card:hover {
				transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12);
			}
			.guia-card:hover .guia-card-brand-img {
				filter: grayscale(0);
			}
			.guia-card .machine-img {
				width: 8rem;
				height: 8rem;
				margin-top: 2.25rem;
			}
			.guia-card-brand {
				font-size: 0.7rem;
				opacity: 0.45;
				font-weight: 600;
				text-transform: uppercase;
				display: none;
			}
			.guia-card-name  {
				font-size: 0.85rem;
				font-weight: 600;
				line-height: 0.9rem;
			}
			.guia-card-pending {
				cursor: default;
			}
			.guia-card-pending:hover {
				transform: none; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
			}
			.guia-badge-pending {
				font-size: 0.7rem;
				font-weight: 600;
				background: var(--primaryopacity);
    			color: var(--primary);
				padding: 0.25rem 0.75rem;
				border-radius: 2rem 0 0 2rem;
				position: absolute;
				right: 0;
				top: 1rem;
				z-index: 1;
			}
			.guia-card-pending img {
				    opacity: 0.5;
			}
			.guia-card-pending .guia-card-name {
				opacity: 0.5;
			}

			.guia-add-card {
				background: #f9f9f9;
				border: 2px dashed #ddd;
				border-radius: 14px;
				padding: 1.2rem;
				width: 12.5rem;
				display: flex;
				flex-direction: column;
				align-items: center;
				justify-content: center;
				gap: 0.5rem;
				cursor: pointer;
				transition: background 0.15s, border-color 0.15s;
				min-height: 15rem;
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
				position: relative; overflow: hidden;
				display: flex; align-items: center; gap: 1.25rem;
				padding: 1.5rem 1.75rem; border-radius: 16px;
				background: linear-gradient(120deg, #fdf3ee 0%, #f7f7f7 65%);
				border: 1px solid #00000010;
			}
			.guia-detail-machine {
				width: 7rem; height: 7rem; flex-shrink: 0; z-index: 1;
				object-fit: contain; border-radius: 12px; background: #fff;
				box-shadow: 0 4px 14px rgba(0,0,0,0.06); padding: 0.4rem; box-sizing: border-box;
			}
			.guia-detail-meta { display: flex; flex-direction: column; gap: 0.15rem; z-index: 1; }
			.guia-detail-eyebrow {
				font-size: 0.68rem; font-weight: 800; letter-spacing: 0.08em;
				text-transform: uppercase; color: #e05a00; margin-bottom: 0.15rem;
			}
			.guia-detail-name  { font-size: 1.4rem; font-weight: 800; line-height: 1.1; color: #1f2937; }
			.guia-detail-brand { font-size: 0.85rem; opacity: 0.55; font-weight: 600; }
			.guia-detail-brandlogo {
				position: absolute; right: 1.5rem; top: 50%; transform: translateY(-50%);
				width: 13rem; max-width: 45%; object-fit: contain; opacity: 0.12;
				filter: grayscale(1); pointer-events: none; z-index: 0;
			}
			.guia-detail-desc  { color: #444; font-size: 0.9rem; line-height: 1.6; white-space: pre-line; }

			/* Advertencia de voltaje (siempre 220V) */
			.guia-voltage-warning {
				display: flex; align-items: center; gap: 1rem;
				padding: 1.1rem 1.5rem; border-radius: 16px;
				background: #fffaf0;
				border: 1px solid #00000010; 
				box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
			}
			.guia-voltage-ico {
				width: 2.75rem; height: 2.75rem; min-width: 2.75rem; border-radius: 50%;
				background: #fdf0d6; color: #c98a00;
				display: flex; align-items: center; justify-content: center;
			}
			.guia-voltage-ico svg { width: 1.35rem; height: 1.35rem; }
			.guia-voltage-text { display: flex; flex-direction: column; gap: 0.15rem; }
			.guia-voltage-title { font-size: 0.98rem; font-weight: 800; color: #1f2937; }
			.guia-voltage-title strong { color: #e05a00; }
			.guia-voltage-sub { font-size: 0.83rem; line-height: 1.5; color: #6b7280; }
			.guia-voltage-sub strong { color: #e05a00; font-weight: 700; }

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
				max-height: 90vh; 
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

			/* Pasos con video incrustado */
			.guia-step-card {
				border: 1px solid #eee; border-radius: 12px; padding: 1rem;
				display: flex; flex-direction: column; gap: 0.75rem;
				box-shadow: 0 2px 8px rgba(0,0,0,0.05);
			}
			.guia-step-head { display: flex; align-items: center; gap: 0.6rem; }
			.guia-step-num {
				flex-shrink: 0; width: 1.8rem; height: 1.8rem; border-radius: 50%;
				background: #e05a00; color: #fff; font-weight: 700; font-size: 0.85rem;
				display: flex; align-items: center; justify-content: center;
			}
			.guia-step-title { font-weight: 700; font-size: 0.95rem; color: #222; }
			.guia-video {
				position: relative; width: 100%; padding-top: 56.25%;
				border-radius: 10px; overflow: hidden; background: #000;
			}
			.guia-video iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
			.guia-step-card img { max-width: 100%; border-radius: 8px; }

			/* Bonus Track - Drive */
			.guia-drive-wrap {
				text-align: center; padding: 1.5rem 1rem; border-radius: 12px;
				background: #fdf3ee; display: flex; flex-direction: column; align-items: center; gap: 0.4rem;
			}
			.guia-drive-title { font-weight: 800; font-size: 1.05rem; color: #222; }
			.guia-drive-sub { font-size: 0.85rem; color: #e05a00; margin: 0 0 0.4rem; }
			.guia-drive-btn {
				display: inline-flex; align-items: center; gap: 0.5rem;
				background: #e05a00; color: #fff !important; text-decoration: none;
				font-weight: 700; padding: 0.8rem 2rem; border-radius: 2rem; transition: opacity .2s;
			}
			.guia-drive-btn:hover { opacity: 0.88; }

			/* Videos del equipo en grilla */
			.guia-video-grid {
				display: grid;
				grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
				gap: 1rem;
			}

			/* ═══ Centro de aprendizaje (wiki por tipo) ═══ */
			.guia-lc {
				display: flex; flex-direction: column; gap: 1.25rem;
				border: 1px solid #00000010; border-radius: 16px;
				padding: 1.5rem; background: #fff; margin-top: 0.5rem;
			}
			.guia-lc-head { display: flex; align-items: center; gap: 0.85rem; }
			.guia-lc-head-ico { font-size: 1.6rem; line-height: 1; }
			.guia-lc-head-title { font-size: 1.2rem; font-weight: 800; color: #1f2937; }
			.guia-lc-head-sub { font-size: 0.85rem; color: #6b7280; line-height: 1.4; }

			.guia-lc-tabs { display: flex; flex-wrap: wrap; gap: 0.6rem; }
			.guia-lc-tab {
				display: inline-flex; align-items: center; gap: 0.45rem;
				background: #fff; border: 1px solid #e4e4e4; border-radius: 12px;
				padding: 0.7rem 1.1rem; font-size: 0.85rem; font-weight: 600;
				color: #4b5563; cursor: pointer; transition: all 0.15s; font-family: inherit;
			}
			.guia-lc-tab:hover { border-color: #e05a00; color: #e05a00; }
			.guia-lc-tab.active {
				background: #fff6ef; border-color: #e05a00; color: #e05a00;
				box-shadow: inset 0 0 0 1px #e05a00;
			}
			.guia-lc-tab-ico { font-size: 1rem; }
			.guia-lc-tab-support { margin-left: auto; }

			.guia-lc-loading { color: #9aa0a6; font-size: 0.88rem; padding: 1.5rem 0; }

			.guia-lc-grid { display: grid; grid-template-columns: 1fr 16rem; gap: 1.5rem; align-items: start; }
			.guia-lc-content { min-width: 0; border: 1px solid #f0f0f0; border-radius: 14px; padding: 1.25rem 1.5rem; }

			.guia-guidehead { display: flex; align-items: center; gap: 0.9rem; }
			.guia-guidehead-ico {
				width: 2.75rem; height: 2.75rem; min-width: 2.75rem; border-radius: 12px;
				background: #fff6ef; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
			}
			.guia-guidehead-title { font-size: 1.05rem; font-weight: 800; color: #1f2937; }
			.guia-guidehead-sub { font-size: 0.83rem; color: #6b7280; line-height: 1.4; }
			.guia-guidehead-meta {
				display: flex; flex-wrap: wrap; gap: 1.25rem; margin: 0.85rem 0 1rem;
				font-size: 0.78rem; color: #9aa0a6; font-weight: 600;
			}

			/* Acordeón */
			.guia-acc { display: flex; flex-direction: column; }
			.guia-acc-item { border-top: 1px solid #f0f0f0; }
			.guia-acc-item:last-child { border-bottom: 1px solid #f0f0f0; }
			.guia-acc-head {
				width: 100%; display: flex; align-items: center; gap: 0.75rem;
				background: none; border: none; cursor: pointer; padding: 0.95rem 0;
				text-align: left; font-family: inherit;
			}
			.guia-acc-num {
				width: 1.5rem; height: 1.5rem; min-width: 1.5rem; border-radius: 50%;
				background: #f3f4f6; color: #6b7280; font-size: 0.75rem; font-weight: 700;
				display: flex; align-items: center; justify-content: center;
			}
			.guia-acc-item.open .guia-acc-num { background: #e05a00; color: #fff; }
			.guia-acc-title { flex: 1; font-size: 0.92rem; font-weight: 700; color: #1f2937; }
			.guia-acc-chev { width: 1.1rem; height: 1.1rem; color: #9aa0a6; transition: transform 0.2s; flex-shrink: 0; }
			.guia-acc-item.open .guia-acc-chev { transform: rotate(180deg); }
			.guia-acc-body { display: none; padding: 0 0 1.1rem 2.25rem; font-size: 0.88rem; color: #444; line-height: 1.65; }
			.guia-acc-item.open .guia-acc-body { display: block; }

			/* Markdown */
			.guia-acc-body p { margin: 0 0 0.7rem; }
			.guia-md-h3 { font-size: 0.92rem; font-weight: 700; color: #1f2937; margin: 1rem 0 0.4rem; }
			.guia-md-h4 { font-size: 0.86rem; font-weight: 700; color: #374151; margin: 0.8rem 0 0.3rem; }
			.guia-md-list { margin: 0 0 0.8rem; padding-left: 1.2rem; }
			.guia-md-list li { list-style: circle; margin-bottom: 0.3rem; }
			.guia-acc-body code { background: #f3f4f6; padding: 0.1rem 0.35rem; border-radius: 5px; font-size: 0.85em; }
			.guia-md-tablewrap { overflow-x: auto; margin: 0 0 0.9rem; }
			.guia-md-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
			.guia-md-table th, .guia-md-table td { border: 1px solid #eee; padding: 0.5rem 0.7rem; text-align: left; }
			.guia-md-table th { background: #fafafa; font-weight: 700; color: #374151; }
			.guia-md-shot {
				display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.4rem;
				border: 1.5px dashed #e0d3c8; border-radius: 12px; background: #fcf7f3;
				padding: 1.5rem 1rem; margin: 0.6rem 0 0.9rem; color: #b08968; text-align: center;
			}
			.guia-md-shot svg { width: 1.6rem; height: 1.6rem; opacity: 0.6; }
			.guia-md-shot span { font-size: 0.8rem; }
			.guia-md-fig { margin: 0.6rem 0 0.9rem; }
			.guia-md-fig img { max-width: 100%; border-radius: 10px; border: 1px solid #eee; }
			.guia-md-fig figcaption { font-size: 0.76rem; color: #9aa0a6; margin-top: 0.35rem; text-align: center; }

			/* TOC */
			.guia-lc-toc {
				position: sticky; top: 7.5rem; border: 1px solid #f0f0f0;
				border-radius: 14px; padding: 1.1rem 1.25rem; background: #fff;
			}
			.guia-lc-toc-title { font-size: 0.85rem; font-weight: 800; color: #1f2937; margin-bottom: 0.75rem; }
			.guia-lc-toc-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.1rem; }
			.guia-lc-toc-list li {
				display: flex; align-items: flex-start; gap: 0.6rem; cursor: pointer;
				font-size: 0.82rem; color: #6b7280; padding: 0.45rem 0.5rem;
				border-radius: 8px; transition: background 0.15s, color 0.15s; line-height: 1.3;
			}
			.guia-lc-toc-list li span {
				width: 1.4rem; height: 1.4rem; min-width: 1.4rem; border-radius: 50%;
				background: #f3f4f6; color: #9aa0a6; font-size: 0.72rem; font-weight: 700;
				display: flex; align-items: center; justify-content: center;
			}
			.guia-lc-toc-list li:hover { background: #faf7f4; color: #1f2937; }
			.guia-lc-toc-list li.active { color: #e05a00; font-weight: 700; }
			.guia-lc-toc-list li.active span { background: #e05a00; color: #fff; }

			/* Bloques de soporte */
			.guia-lc-support { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1rem; }
			.guia-sup-card {
				display: flex; align-items: center; gap: 0.85rem; text-decoration: none;
				border: 1px solid #00000010; border-radius: 14px; padding: 1.1rem 1.25rem;
				color: inherit; transition: box-shadow 0.15s, transform 0.1s; background: #fff;
			}
			.guia-sup-card:hover { box-shadow: 0 6px 18px rgba(0,0,0,.07); transform: translateY(-1px); }
			.guia-sup-ico {
				width: 2.5rem; height: 2.5rem; min-width: 2.5rem; border-radius: 12px;
				background: #fff6ef; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
			}
			.guia-sup-wa .guia-sup-ico { background: #e7f8ef; }
			.guia-sup-txt { flex: 1; min-width: 0; }
			.guia-sup-title { font-weight: 700; font-size: 0.9rem; color: #1f2937; }
			.guia-sup-sub { font-size: 0.78rem; color: #9aa0a6; line-height: 1.3; }
			.guia-sup-chev { color: #c9c9c9; font-size: 1.3rem; line-height: 1; }
			.guia-sup-panel h4 { margin: 0 0 0.5rem; font-size: 1rem; font-weight: 800; color: #1f2937; }
			.guia-sup-panel p { font-size: 0.88rem; color: #555; margin: 0 0 0.8rem; }

			@media (max-width: 900px) {
				.guia-lc-grid { grid-template-columns: 1fr; }
				.guia-lc-toc { position: static; }
				.guia-lc-tab-support { margin-left: 0; }
			}
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
				const BRANDS_URL = `${INTRANET}/static/images/uploads/brands/`;

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
						const isApproved = g.status === 'approved';
						const locked     = !isApproved; // pending o in_review: aún sin acceso
						const badge      = locked ? 'En revisión' : '';
						const card = document.createElement('div');
						card.className = 'guia-card' + (locked ? ' guia-card-pending' : '');
						card.innerHTML = `
							${badge ? `<div class="guia-badge-pending">${badge}</div>` : ''}
							<div class="guia-card-brand-img"><img src="${BRANDS_URL}${g.brand_image}" alt="${g.brand_name}" style="width:${(g.brand_scale || 1) * 100}%"></div>
							<img class="machine-img" src="${MACHINES_URL}${g.machine_image}" alt="${g.machine_name}">
							<div class="guia-card-name">${g.machine_name}</div>
						`;
						if (isApproved) {
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
					const _bimg = document.getElementById('guia-detail-brand-img');
					if (guide.brand_image) { _bimg.src = `${BRANDS_URL}${guide.brand_image}`; _bimg.style.display = ''; }
					else { _bimg.style.display = 'none'; }
					document.getElementById('guia-detail-desc').textContent  = '';
					document.getElementById('guia-detail-items').innerHTML   = '<p style="opacity:0.4;font-size:0.85rem">Cargando contenido...</p>';

					grid.style.display   = 'none';
					detail.style.display = 'flex';

					try {
						const r = await fetch(`${API}/guide/content/${guide.machine_id}?wp_user_id=${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						renderGuideContent(j.data || {}, guide);
					} catch(e) {
						document.getElementById('guia-detail-items').innerHTML = '<p style="opacity:0.4;font-size:0.85rem">Sin contenido disponible.</p>';
					}
				}

				function youtubeId(url) {
					if (!url) return null;
					const res = [
						/youtu\.be\/([\w-]{11})/,
						/youtube\.com\/watch\?v=([\w-]{11})/,
						/youtube\.com\/embed\/([\w-]{11})/,
						/youtube\.com\/shorts\/([\w-]{11})/,
						/[?&]v=([\w-]{11})/,
					];
					for (const re of res) { const m = url.match(re); if (m) return m[1]; }
					return null;
				}

				function renderGuideContent(content, guide) {
					const machine_id = guide.machine_id;
					document.getElementById('guia-detail-desc').textContent = content.description || '';
					const container = document.getElementById('guia-detail-items');
					container.innerHTML = '';

					// El antiguo Bonus Track (link de Drive) ya no se usa; el contenido de
					// aprendizaje se arma desde la wiki por tipo de máquina (ver appendLearningCenter)
					const items  = (content.items || []).filter(it => it.type !== 'drive');
					const videos = items.filter(it => it.type === 'video' && it.url);
					const others = items.filter(it => !(it.type === 'video' && it.url));

					// Videos del equipo (unboxing, calibración, carga de filamento...) en grilla
					if (videos.length) {
						const grid = document.createElement('div');
						grid.className = 'guia-video-grid';
						videos.forEach((item, idx) => {
							const id = youtubeId(item.url);
							const media = id
								? `<div class="guia-video"><iframe src="https://www.youtube.com/embed/${id}" title="${item.title || ''}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>`
								: `<a href="${item.url}" target="_blank" rel="noopener" class="guia-item-link">Ver video</a>`;
							const card = document.createElement('div');
							card.className = 'guia-step-card';
							card.innerHTML = `
								<div class="guia-step-head">
									<span class="guia-step-num">${idx + 1}</span>
									<span class="guia-step-title">${item.title || ''}</span>
								</div>
								${media}`;
							grid.appendChild(card);
						});
						container.appendChild(grid);
					}

					// Otros recursos cargados por el equipo (imágenes / PDFs)
					others.forEach(item => {
						const card = document.createElement('div');
						card.className = 'guia-step-card';
						if (item.type === 'image' && item.filename) {
							card.innerHTML = `<div class="guia-step-title">${item.title || ''}</div>
								<img src="${API}/guide/media/${item.filename}?wp_user_id=${WP_USER_ID}&machine_id=${machine_id}" alt="${item.title || ''}">`;
						} else if (item.type === 'pdf' && item.filename) {
							card.innerHTML = `<div class="guia-step-title">${item.title || ''}</div>
								<a href="${API}/guide/media/${item.filename}?wp_user_id=${WP_USER_ID}&machine_id=${machine_id}" target="_blank" rel="noopener" class="guia-item-link">
									<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
									Ver PDF
								</a>`;
						} else {
							return;
						}
						container.appendChild(card);
					});

					// Centro de aprendizaje (wiki por tipo de máquina: FDM / LCD)
					appendLearningCenter(container, guide);
				}

				// ── Centro de aprendizaje: wiki por tipo de máquina (FDM / LCD) ──
				// El backend lee y parsea las guías (static/guide/<tipo>/*.md) y entrega el
				// JSON completo en /guide/wiki/<machine_id>; aquí solo se renderiza.
				const WA_PHONE = '51970539751';

				function escHtml(t) {
					return (t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
				}

				function tabIcon(tab) {
					const t = (tab.title || '').toLowerCase();
					if (t.includes('error'))                                              return '⚠️';
					if (t.includes('tip'))                                                return '🧪';
					if (t.includes('cad') || t.includes('modelo') || t.includes('diseño')) return '📦';
					if (t.includes('segur'))                                              return '🛡️';
					if (t.includes('postpro') || t.includes('lavado'))                    return '🧼';
					if (t.includes('tecnolog'))                                           return '🔬';
					return '📘';
				}

				function renderGuidePanel(panelEl, tab) {
					const mins = tab.reading_min || 2;
					const sections = tab.sections || [];
					const toc = sections.map((s, i) => `<li data-sec="${i}"${i === 0 ? ' class="active"' : ''}><span>${i + 1}</span>${escHtml(s.title)}</li>`).join('');
					const acc = sections.map((s, i) => `
						<div class="guia-acc-item${i === 0 ? ' open' : ''}" data-sec="${i}">
							<button class="guia-acc-head">
								<span class="guia-acc-num">${i + 1}</span>
								<span class="guia-acc-title">${escHtml(s.title)}</span>
								<svg class="guia-acc-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
							</button>
							<div class="guia-acc-body">${s.html || ''}</div>
						</div>`).join('');
					const subtitle = tab.intro ? escHtml(tab.intro.split('\n')[0]) : '';
					panelEl.innerHTML = `
						<div class="guia-lc-grid">
							<div class="guia-lc-content">
								<div class="guia-guidehead">
									<div class="guia-guidehead-ico">${tabIcon(tab)}</div>
									<div>
										<div class="guia-guidehead-title">${escHtml(tab.title)}</div>
										<div class="guia-guidehead-sub">${subtitle}</div>
									</div>
								</div>
								<div class="guia-guidehead-meta">
									<span>⏱️ Lectura: ${mins} min</span>
									<span>📶 Nivel: ${escHtml(tab.level || 'Básico')}</span>
								</div>
								<div class="guia-acc">${acc}</div>
							</div>
							<aside class="guia-lc-toc">
								<div class="guia-lc-toc-title">📑 En esta guía</div>
								<ol class="guia-lc-toc-list">${toc}</ol>
							</aside>
						</div>`;

					function syncToc() {
						const openItem = panelEl.querySelector('.guia-acc-item.open');
						const idx = openItem ? openItem.getAttribute('data-sec') : null;
						panelEl.querySelectorAll('.guia-lc-toc-list li').forEach(li => li.classList.toggle('active', li.getAttribute('data-sec') === idx));
					}
					panelEl.querySelectorAll('.guia-acc-head').forEach(h => {
						h.addEventListener('click', () => {
							const item = h.closest('.guia-acc-item');
							const wasOpen = item.classList.contains('open');
							panelEl.querySelectorAll('.guia-acc-item').forEach(x => x.classList.remove('open'));
							if (!wasOpen) item.classList.add('open');
							syncToc();
						});
					});
					panelEl.querySelectorAll('.guia-lc-toc-list li').forEach(li => {
						li.addEventListener('click', () => {
							const idx = li.getAttribute('data-sec');
							const item = panelEl.querySelector(`.guia-acc-item[data-sec="${idx}"]`);
							panelEl.querySelectorAll('.guia-acc-item').forEach(x => x.classList.remove('open'));
							item.classList.add('open');
							syncToc();
							item.scrollIntoView({ behavior: 'smooth', block: 'center' });
						});
					});
				}

				function supportPanelHtml() {
					return `<div class="guia-sup-panel">
						<h4>Soporte y capacitación</h4>
						<p>¿Tienes dudas con tu equipo o con tu primera impresión? Nuestro equipo te acompaña en todo el proceso.</p>
						<ul class="guia-md-list">
							<li><strong>WhatsApp:</strong> +51 970 539 751 (atención únicamente por chat). Envíanos fotos o videos del problema para orientarte mejor.</li>
							<li><strong>Capacitación virtual:</strong> agenda una sesión para aprender el flujo completo de impresión.</li>
							<li><strong>K3D FAB:</strong> impresiones 3D a pedido y repuestos cuando los necesites.</li>
						</ul>
					</div>`;
				}

				function renderSupportBlocks(el) {
					el.innerHTML = `
						<a class="guia-sup-card guia-sup-wa" href="https://wa.me/${WA_PHONE}" target="_blank" rel="noopener">
							<div class="guia-sup-ico">🟢</div>
							<div class="guia-sup-txt"><div class="guia-sup-title">Soporte técnico por WhatsApp</div><div class="guia-sup-sub">Atención rápida para resolver tus dudas.</div></div>
							<span class="guia-sup-chev">›</span>
						</a>
						<a class="guia-sup-card" href="/cursos/">
							<div class="guia-sup-ico">🎓</div>
							<div class="guia-sup-txt"><div class="guia-sup-title">Potencia tus conocimientos</div><div class="guia-sup-sub">Cursos con contenido de calidad.</div></div>
							<span class="guia-sup-chev">›</span>
						</a>
						<a class="guia-sup-card" href="/stl/">
							<div class="guia-sup-ico">🧩</div>
							<div class="guia-sup-txt"><div class="guia-sup-title">K3D FAB</div><div class="guia-sup-sub">Diseños listos para imprimir.</div></div>
							<span class="guia-sup-chev">›</span>
						</a>
						`;
				}

				async function appendLearningCenter(container, guide) {
					const wrap = document.createElement('div');
					wrap.className = 'guia-lc';
					wrap.innerHTML = `
						<div class="guia-lc-head">
							<span class="guia-lc-head-ico">🎓</span>
							<div>
								<div class="guia-lc-head-title">Centro de aprendizaje</div>
								<div class="guia-lc-head-sub">Complementa tu capacitación con guías prácticas, soluciones y recursos para imprimir mejor desde el primer día.</div>
							</div>
						</div>
						<div class="guia-lc-tabs"></div>
						<div class="guia-lc-panel"><p class="guia-lc-loading">Cargando guías...</p></div>
						<div class="guia-lc-support"></div>`;
					container.appendChild(wrap);

					const tabsEl  = wrap.querySelector('.guia-lc-tabs');
					const panelEl = wrap.querySelector('.guia-lc-panel');
					renderSupportBlocks(wrap.querySelector('.guia-lc-support'));

					let data = null;
					try {
						const r = await fetch(`${API}/guide/wiki/${guide.machine_id}?wp_user_id=${WP_USER_ID}`, { headers: { 'X-No-Toast': '1' } });
						const j = await r.json();
						data = j.data;
					} catch (e) {}

					if (!data || !Array.isArray(data.tabs) || !data.tabs.length) { wrap.remove(); return; }

					wrap.querySelector('.guia-lc-head-title').textContent = data.label || 'Centro de aprendizaje';

					data.tabs.forEach((tab, idx) => {
						const btn = document.createElement('button');
						btn.className = 'guia-lc-tab' + (idx === 0 ? ' active' : '');
						btn.innerHTML = `<span class="guia-lc-tab-ico">${tabIcon(tab)}</span>${escHtml(tab.title)}`;
						btn.addEventListener('click', () => selectTab(idx));
						tabsEl.appendChild(btn);
					});

					function selectTab(idx) {
						tabsEl.querySelectorAll('.guia-lc-tab').forEach(b => b.classList.remove('active'));
						tabsEl.querySelectorAll('.guia-lc-tab')[idx].classList.add('active');
						renderGuidePanel(panelEl, data.tabs[idx]);
					}
					selectTab(0);
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
					document.getElementById('guia-invoice-input').value = '';
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

					const invoice = document.getElementById('guia-invoice-input').value.trim();
					if (!invoice) {
						errEl.textContent = 'Ingresa el número de boleta o factura.';
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
					fd.append('invoice_number', invoice);
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
						document.getElementById('guias-grid').style.display = 'grid';
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
			<div id="section-pedidos" class="section-content" style="display:none;">
				<?php
					$kd_orders = wc_get_orders( array(
						'customer_id' => get_current_user_id(),
						'limit'       => -1,
						'orderby'     => 'date',
						'order'       => 'DESC',
					) );

					$kd_oicons = array(
						'bag'     => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
						'check'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>',
						'clock'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 7 12 12 15 14"/></svg>',
						'x'       => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
						'refresh' => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>',
						'chev'    => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
						'cal'     => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
					);
					$kd_smeta = array(
						'completed'  => array( 'check',   'kd-st-completed' ),
						'processing' => array( 'refresh', 'kd-st-processing' ),
						'on-hold'    => array( 'clock',   'kd-st-hold' ),
						'pending'    => array( 'clock',   'kd-st-hold' ),
						'cancelled'  => array( 'x',       'kd-st-cancelled' ),
						'failed'     => array( 'x',       'kd-st-cancelled' ),
						'refunded'   => array( 'refresh', 'kd-st-refunded' ),
					);

					$kd_present = array();
					foreach ( $kd_orders as $kd_o ) {
						$kd_present[ $kd_o->get_status() ] = wc_get_order_status_name( $kd_o->get_status() );
					}
				?>
				<div class="kd-orders-head">
					<h2>Mis pedidos</h2>
					<?php if ( $kd_orders ) : ?>
						<div class="kd-orders-filter">
							<?php echo $kd_oicons['cal']; ?>
							<select id="kd-orders-filter-select">
								<option value="">Todos los pedidos</option>
								<?php foreach ( $kd_present as $kd_slug => $kd_label ) : ?>
									<option value="<?php echo esc_attr( $kd_slug ); ?>"><?php echo esc_html( $kd_label ); ?></option>
								<?php endforeach; ?>
							</select>
						</div>
					<?php endif; ?>
				</div>

				<?php if ( $kd_orders ) : ?>
					<div class="kd-orders-list">
						<?php foreach ( $kd_orders as $kd_o ) :
							$kd_slug = $kd_o->get_status();
							$kd_m    = isset( $kd_smeta[ $kd_slug ] ) ? $kd_smeta[ $kd_slug ] : array( 'clock', 'kd-st-hold' );
						?>
							<a class="kd-order-card" data-status="<?php echo esc_attr( $kd_slug ); ?>" href="<?php echo esc_url( $kd_o->get_view_order_url() ); ?>">
								<span class="kd-order-ico"><?php echo $kd_oicons['bag']; ?></span>
								<div class="kd-order-main">
									<span class="kd-order-num">Pedido #<?php echo esc_html( $kd_o->get_order_number() ); ?></span>
									<span class="kd-order-date"><?php echo esc_html( wc_format_datetime( $kd_o->get_date_created(), 'j \d\e F \d\e Y' ) ); ?></span>
								</div>
								<span class="kd-order-status <?php echo esc_attr( $kd_m[1] ); ?>"><?php echo $kd_oicons[ $kd_m[0] ]; ?><span><?php echo esc_html( wc_get_order_status_name( $kd_slug ) ); ?></span></span>
								<div class="kd-order-totals">
									<span class="kd-order-total-lbl">Total</span>
									<span class="kd-order-total"><?php echo wp_kses_post( $kd_o->get_formatted_order_total() ); ?></span>
								</div>
								<span class="kd-order-chev"><?php echo $kd_oicons['chev']; ?></span>
							</a>
						<?php endforeach; ?>
					</div>
				<?php else : ?>
					<p class="kd-orders-empty">Aún no tienes pedidos.</p>
				<?php endif; ?>

				<script>
				(function(){
					var sel = document.getElementById('kd-orders-filter-select');
					if (!sel) return;
					sel.addEventListener('change', function(){
						var v = this.value;
						document.querySelectorAll('#section-pedidos .kd-order-card').forEach(function(c){
							c.style.display = (!v || c.getAttribute('data-status') === v) ? '' : 'none';
						});
					});
				})();
				</script>
			</div>
			<div id="kd-wc-content" style="display:<?php echo $kd_is_wc ? 'block' : 'none'; ?>;">
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
