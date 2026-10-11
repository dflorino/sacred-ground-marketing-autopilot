<?php
/**
 * Plugin Name: Sacred Ground Helper
 * Description: Ordinary (deactivatable) home for Sacred Ground shop customizations. Replaces the former sg-* must-use plugins.
 * Version: 1.0.41
 * Author: Sacred Ground
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Text Domain: sacred-ground-helper
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'SG_HELPER_VERSION', '1.0.41' );
define( 'SG_HELPER_FILE', __FILE__ );
define( 'SG_HELPER_DIR', plugin_dir_path( __FILE__ ) );

$sg_helper_modules = array(
	'shop-ui-polish.php',
	'shop-category-nav.php',
	'shop-performance.php',
	'shop-price-display.php',
	'checkout-simplify.php',
	'product-substitution.php',
	'shop-contact.php',
	'cart-ui.php',
	'booking-guest-identity.php',
	'booking-admin-emails.php',
	'booking-admin-payment-ui.php',
	'booking-version-pin.php',
	'calendar-embed.php',
	'booking-cancel-reschedule-sms.php',
	'booking-page-ui.php',
	'my-account-ui.php',
	'your-calendar-ui.php',
	'consent-waiver.php',
	'tec-fluent-trap-guard.php',
	'practitioner-bio-photos.php',
	'ask-deneene.php',
	'ask-lisa-maria.php',
);

foreach ( $sg_helper_modules as $sg_helper_module ) {
	$sg_helper_path = SG_HELPER_DIR . 'includes/' . $sg_helper_module;
	if ( ! file_exists( $sg_helper_path ) ) {
		continue;
	}
	try {
		require_once $sg_helper_path;
	} catch ( Throwable $e ) {
		// Fail soft: skip broken module rather than take down the site.
		if ( function_exists( 'error_log' ) ) {
			error_log( 'Sacred Ground Helper skipped module ' . $sg_helper_module . ': ' . $e->getMessage() );
		}
	}
}
