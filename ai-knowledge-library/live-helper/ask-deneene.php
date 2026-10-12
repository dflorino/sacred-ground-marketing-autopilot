<?php
/**
 * Ask Deneene — public-page talking box.
 *
 * On public pages only. Never on individual practitioner pages,
 * booking pages, cart, checkout, or account.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'SG_ASK_DENEENE_VOICE_FALLBACK', 'vSbSsSjeNo7FMkmvwZJs' );
define( 'SG_ASK_DENEENE_PHOTO', 'https://shopsacredground.com/wp-content/uploads/deneene-official-face.jpg' );
define( 'SG_ASK_DENEENE_MODEL', 'openai/gpt-4.1-mini' );

/**
 * Pages that are one person, not the public shop.
 *
 * @return string[]
 */
function sg_ask_deneene_blocked_slugs() {
	return array(
		'adie-11',
		'amber-11',
		'andre-11',
		'andrea-11',
		'cheryl-11',
		'deneene-11',
		'eve-11',
		'jill-11',
		'karen-11',
		'kate-11',
		'linn-11',
		'lisa-maria-11',
		'lisa-seyring-11',
		'lita-11',
		'mary-11',
		'mother-lotus-11',
		'richard-11',
		'robert-11',
		'janel',
		'janel-akashic-records-angel-card-reader',
		'janel-crystal',
		'lisa-astrology-v5-final',
		'melissa',
		'melissa-v5',
		'melissa-art',
		'melissa-circle',
		'melissa-class',
		'melissa-whispers',
		'rose',
		'rose-passarella',
		'rose-v5-working',
		'rose-vision',
		'rose-sound',
		'sherry',
		'karen-akashic',
	);
}

/**
 * Whether the live bubble may print on this request.
 *
 * @return bool
 */
function sg_ask_deneene_should_show() {
	if ( is_admin() || wp_doing_ajax() || wp_doing_cron() || is_feed() ) {
		return false;
	}
	if ( function_exists( 'wp_is_json_request' ) && wp_is_json_request() ) {
		return false;
	}
	if ( function_exists( 'is_cart' ) && is_cart() ) {
		return false;
	}
	if ( function_exists( 'is_checkout' ) && is_checkout() ) {
		return false;
	}
	if ( function_exists( 'is_account_page' ) && is_account_page() ) {
		return false;
	}

	$path = (string) parse_url( isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '', PHP_URL_PATH );
	$path = trim( $path, '/' );
	$first = explode( '/', $path );
	$first = strtolower( (string) ( $first[0] ?? '' ) );

	if ( in_array( $first, array( 'wp-admin', 'wp-login.php', 'wp-json', 'cart', 'checkout', 'my-account', 'book' ), true ) ) {
		return false;
	}

	$slug = '';
	$obj  = get_queried_object();
	if ( $obj && ! empty( $obj->post_name ) ) {
		$slug = strtolower( (string) $obj->post_name );
	} elseif ( $path !== '' ) {
		$bits = explode( '/', $path );
		$slug = strtolower( (string) end( $bits ) );
	}

	if ( $slug === '' ) {
		return true;
	}
	if ( in_array( $slug, sg_ask_deneene_blocked_slugs(), true ) ) {
		return false;
	}
	if ( $slug !== 'experiences-11' && substr( $slug, -3 ) === '-11' ) {
		return false;
	}

	return true;
}

/**
 * Load packed cards + question map.
 *
 * @return array{cards:array,by_id:array,questions:array}
 */
function sg_ask_deneene_library() {
	static $pack = null;
	if ( is_array( $pack ) ) {
		return $pack;
	}
	$pack = array(
		'cards'     => array(),
		'by_id'     => array(),
		'questions' => array(),
	);
	$dir   = dirname( __FILE__ );
	$cards = $dir . '/ask-deneene-cards.json';
	$qs    = $dir . '/ask-deneene-questions.json';
	if ( is_readable( $cards ) ) {
		$data = json_decode( (string) file_get_contents( $cards ), true );
		if ( is_array( $data ) ) {
			$pack['cards'] = $data;
			foreach ( $data as $card ) {
				if ( ! empty( $card['card_id'] ) ) {
					$pack['by_id'][ $card['card_id'] ] = $card;
				}
			}
		}
	}
	if ( is_readable( $qs ) ) {
		$data = json_decode( (string) file_get_contents( $qs ), true );
		if ( is_array( $data ) ) {
			$pack['questions'] = $data;
		}
	}
	return $pack;
}

/**
 * @param string $text Text.
 * @return string[]
 */
function sg_ask_deneene_tokens( $text ) {
	$stop = array(
		'a' => 1, 'an' => 1, 'the' => 1, 'is' => 1, 'are' => 1, 'am' => 1,
		'i' => 1, 'im' => 1, "i'm" => 1, 'me' => 1, 'my' => 1, 'you' => 1,
		'your' => 1, 'we' => 1, 'do' => 1, 'does' => 1, 'what' => 1, 'who' => 1,
		'how' => 1, 'where' => 1, 'when' => 1, 'can' => 1, 'to' => 1, 'for' => 1,
		'of' => 1, 'and' => 1, 'or' => 1, 'in' => 1, 'on' => 1, 'at' => 1,
		'it' => 1, 'this' => 1, 'that' => 1, 'with' => 1, 'about' => 1,
	);
	preg_match_all( "/[a-z0-9']+/", strtolower( (string) $text ), $m );
	$out = array();
	foreach ( (array) $m[0] as $t ) {
		if ( strlen( $t ) > 1 && ! isset( $stop[ $t ] ) ) {
			$out[ $t ] = 1;
		}
	}
	return array_keys( $out );
}

/**
 * @param array  $card     Card.
 * @param string $question Question.
 * @param array  $q_tokens Tokens.
 * @return int
 */
function sg_ask_deneene_score( $card, $question, $q_tokens ) {
	$q     = strtolower( (string) $question );
	$score = 0;
	foreach ( (array) ( $card['keywords'] ?? array() ) as $kw ) {
		$k = strtolower( trim( (string) $kw ) );
		if ( $k !== '' && strpos( $q, $k ) !== false ) {
			$score += 10 + min( strlen( $k ), 12 );
		}
	}
	$q_set = array_fill_keys( $q_tokens, 1 );
	foreach ( (array) ( $card['visitor_questions'] ?? array() ) as $vq ) {
		$v = strtolower( (string) $vq );
		if ( $v === $q || ( $v !== '' && strpos( $q, $v ) !== false ) || ( $q !== '' && strpos( $v, $q ) !== false ) ) {
			$score += 24;
		}
		$overlap = 0;
		foreach ( sg_ask_deneene_tokens( $v ) as $t ) {
			if ( isset( $q_set[ $t ] ) ) {
				$overlap++;
			}
		}
		if ( $overlap ) {
			$score += $overlap * 3;
		}
	}
	$title = strtolower( (string) ( $card['title'] ?? '' ) );
	if ( $title !== '' && strpos( $q, $title ) !== false ) {
		$score += 16;
	}
	foreach ( sg_ask_deneene_tokens( $title ) as $t ) {
		if ( isset( $q_set[ $t ] ) ) {
			$score += 2;
		}
	}
	return $score;
}

/**
 * @param string $question Question.
 * @return array
 */
function sg_ask_deneene_select( $question ) {
	$lib   = sg_ask_deneene_library();
	$by_id = $lib['by_id'];
	$q     = trim( (string) $question );
	$ql    = strtolower( $q );
	$tok   = sg_ask_deneene_tokens( $q );
	$picked = array();

	$add = static function ( $cid ) use ( &$picked, $by_id ) {
		$cid = (string) $cid;
		if ( $cid !== '' && isset( $by_id[ $cid ] ) && ! in_array( $cid, $picked, true ) ) {
			$picked[] = $cid;
		}
	};

	foreach ( array( 'SG-VOICE-IDENTITY', 'SG-RULE-NO-DEATH', 'SG-KNOW-ABOUT', 'SG-KNOW-VISIT', 'SG-PRAC-DENEENE', 'SG-PRAC-LISAMARIA' ) as $cid ) {
		$add( $cid );
	}
	if ( strpos( $ql, 'lisa maria' ) !== false || strpos( $ql, 'lisamaria' ) !== false || strpos( $ql, 'lisa-maria' ) !== false ) {
		$add( 'SG-PRAC-LISAMARIA' );
	}

	foreach ( $lib['questions'] as $row ) {
		$rq = strtolower( (string) ( $row['q'] ?? '' ) );
		if ( $rq === '' ) {
			continue;
		}
		if ( $rq === $ql || strpos( $ql, $rq ) !== false || strpos( $rq, $ql ) !== false ) {
			$add( $row['card_id'] ?? '' );
			continue;
		}
		$overlap = 0;
		$q_set   = array_fill_keys( $tok, 1 );
		foreach ( sg_ask_deneene_tokens( $rq ) as $t ) {
			if ( isset( $q_set[ $t ] ) ) {
				$overlap++;
			}
		}
		if ( $overlap >= 2 ) {
			$add( $row['card_id'] ?? '' );
		}
	}

	$ranked = array();
	foreach ( $lib['cards'] as $card ) {
		$cid = (string) ( $card['card_id'] ?? '' );
		if ( $cid === '' ) {
			continue;
		}
		$ranked[] = array( sg_ask_deneene_score( $card, $q, $tok ), $cid );
	}
	usort(
		$ranked,
		static function ( $a, $b ) {
			return $b[0] <=> $a[0];
		}
	);
	foreach ( $ranked as $row ) {
		if ( $row[0] < 6 ) {
			break;
		}
		$add( $row[1] );
		if ( count( $picked ) >= 15 ) {
			break;
		}
	}

	foreach ( $picked as $cid ) {
		foreach ( array_slice( (array) ( $by_id[ $cid ]['related_cards'] ?? array() ), 0, 2 ) as $other ) {
			if ( count( $picked ) >= 19 ) {
				break 2;
			}
			$add( $other );
		}
	}

	$out = array();
	foreach ( $picked as $cid ) {
		$out[] = $by_id[ $cid ];
	}
	return $out;
}

/**
 * @param string $hm HH:MM.
 * @return string
 */
function sg_ask_deneene_clock( $hm ) {
	$parts = explode( ':', (string) $hm );
	if ( count( $parts ) < 2 || ! is_numeric( $parts[0] ) ) {
		return (string) $hm;
	}
	$hour   = (int) $parts[0];
	$minute = $parts[1];
	$suffix = $hour < 12 ? 'AM' : 'PM';
	$hour12 = $hour % 12;
	if ( $hour12 === 0 ) {
		$hour12 = 12;
	}
	if ( $minute === '00' ) {
		return $hour12 . ' ' . $suffix;
	}
	return $hour12 . ':' . $minute . ' ' . $suffix;
}

/**
 * Next 7 Chicago days from TEC. No prices. No URLs.
 *
 * @return string
 */
function sg_ask_deneene_events() {
	$fail = 'LIVE CALENDAR: lookup failed. Tell them that is on Calendar in the menu. Do not read a website address.';
	if ( ! function_exists( 'tribe_get_events' ) ) {
		return $fail;
	}
	try {
		$tz    = new DateTimeZone( 'America/Chicago' );
		$now   = new DateTimeImmutable( 'now', $tz );
		$end   = $now->modify( '+7 days' )->setTime( 23, 59, 59 );
		$events = tribe_get_events(
			array(
				'start_date'     => $now->format( 'Y-m-d H:i:s' ),
				'end_date'       => $end->format( 'Y-m-d H:i:s' ),
				'posts_per_page' => 25,
			)
		);
	} catch ( Throwable $e ) {
		return $fail;
	}
	$lines = array();
	$seen  = array();
	foreach ( (array) $events as $ev ) {
		$title = trim( preg_replace( '/\s+/', ' ', wp_strip_all_tags( get_the_title( $ev ) ) ) );
		$start = '';
		$stop  = '';
		if ( function_exists( 'tribe_get_start_date' ) ) {
			$start = (string) tribe_get_start_date( $ev, true, 'Y-m-d H:i:s' );
			$stop  = (string) tribe_get_end_date( $ev, true, 'H:i' );
		}
		if ( $start === '' ) {
			continue;
		}
		$key = $start . '|' . $title;
		if ( isset( $seen[ $key ] ) ) {
			continue;
		}
		$seen[ $key ] = 1;
		try {
			$dt   = new DateTimeImmutable( $start, new DateTimeZone( 'America/Chicago' ) );
			$when = $dt->format( 'l, F j' );
			$hm   = $dt->format( 'H:i' );
		} catch ( Exception $e ) {
			continue;
		}
		$clock = sg_ask_deneene_clock( $hm );
		if ( $stop !== '' ) {
			$clock .= ' to ' . sg_ask_deneene_clock( $stop );
		}
		$lines[] = '- ' . $when . ' · ' . $clock . ' · ' . $title;
	}
	if ( ! $lines ) {
		return 'LIVE CALENDAR (next 7 Chicago days): nothing listed. Say you cannot see a live list. That is on Calendar in the menu. Do not read a website address.';
	}
	return "LIVE CALENDAR from The Events Calendar. America/Chicago. No prices. Do not invent a seat count or a cost. Tell them they can find this on Calendar in the menu. Do not read a website address.\n" . implode( "\n", $lines );
}

/**
 * @param array $card Card.
 * @return string
 */
function sg_ask_deneene_format_card( $card ) {
	$lines = array(
		'### ' . ( $card['card_id'] ?? '' ) . ' — ' . ( $card['title'] ?? '' ),
		(string) ( $card['answer'] ?? '' ),
		'Say it like: ' . ( $card['voice_response'] ?? '' ),
		'On the nav: ' . ( $card['nav'] ?? 'the menu' ),
	);
	$page = (string) ( $card['page'] ?? '' );
	if ( $page !== '' ) {
		$lines[] = 'Pressable page: ' . $page;
	}
	foreach ( (array) ( $card['booking'] ?? array() ) as $row ) {
		if ( is_string( $row ) && $row !== '' ) {
			$lines[] = 'Pressable booking: ' . $row;
			continue;
		}
		$url = (string) ( $row['url'] ?? '' );
		if ( $url === '' ) {
			continue;
		}
		$lab = (string) ( $row['label'] ?? 'Book' );
		$lines[] = 'Pressable booking (' . $lab . '): ' . $url;
	}
	return implode( "\n", $lines );
}

/**
 * @param string $url URL.
 * @return string
 */
function sg_ask_deneene_safe_url( $url ) {
	$url = esc_url_raw( (string) $url );
	if ( $url === '' ) {
		return '';
	}
	$host = strtolower( (string) wp_parse_url( $url, PHP_URL_HOST ) );
	if ( $host !== 'shopsacredground.com' && $host !== 'www.shopsacredground.com' ) {
		return '';
	}
	return $url;
}

/**
 * @param string $question Question.
 * @return array<int,array{label:string,url:string}>
 */
function sg_ask_deneene_pressable_links( $question ) {
	$ql   = strtolower( (string) $question );
	$out  = array();
	$seen = array();
	foreach ( sg_ask_deneene_select( $question ) as $card ) {
		$cid = (string) ( $card['card_id'] ?? '' );
		if ( strpos( $cid, 'SG-PRAC-' ) !== 0 ) {
			continue;
		}
		$title = trim( (string) ( $card['title'] ?? '' ) );
		$tl    = strtolower( $title );
		$hit   = false;
		if ( $cid === 'SG-PRAC-LISAMARIA' ) {
			$hit = ( strpos( $ql, 'lisa maria' ) !== false || strpos( $ql, 'lisamaria' ) !== false || strpos( $ql, 'lisa-maria' ) !== false );
		} elseif ( $cid === 'SG-PRAC-LISA' ) {
			$hit = ( strpos( $ql, 'lisa' ) !== false && strpos( $ql, 'maria' ) === false && strpos( $ql, 'seyring' ) === false );
		} elseif ( $cid === 'SG-PRAC-LISAS' ) {
			$hit = ( strpos( $ql, 'seyring' ) !== false || strpos( $ql, 'lisa seyring' ) !== false );
		} elseif ( $tl !== '' && strpos( $ql, $tl ) !== false ) {
			$hit = true;
		} else {
			$first = strtolower( (string) strtok( $title, ' ' ) );
			if ( $first !== '' && preg_match( '/\b' . preg_quote( $first, '/' ) . '\b/', $ql ) ) {
				$hit = true;
			}
		}
		if ( ! $hit ) {
			continue;
		}
		$page = sg_ask_deneene_safe_url( $card['page'] ?? '' );
		if ( $page !== '' && ! isset( $seen[ $page ] ) ) {
			$seen[ $page ] = 1;
			$out[]         = array(
				'label' => $title !== '' ? $title . "'s page" : 'Their page',
				'url'   => $page,
			);
		}
		foreach ( (array) ( $card['booking'] ?? array() ) as $row ) {
			if ( is_string( $row ) ) {
				$url = sg_ask_deneene_safe_url( $row );
				$lab = $title !== '' ? 'Book ' . $title : 'Book a time';
			} else {
				$url = sg_ask_deneene_safe_url( $row['url'] ?? '' );
				$lab = trim( (string) ( $row['label'] ?? '' ) );
				if ( $lab === '' ) {
					$lab = $title !== '' ? 'Book ' . $title : 'Book a time';
				} elseif ( $title !== '' && stripos( $lab, 'book' ) !== 0 ) {
					$lab = 'Book ' . $title . ' — ' . $lab;
				}
			}
			if ( $url !== '' && ! isset( $seen[ $url ] ) ) {
				$seen[ $url ] = 1;
				$out[]        = array(
					'label' => $lab,
					'url'   => $url,
				);
			}
		}
	}
	return $out;
}

/**
 * @param string $question Question.
 * @return string
 */
function sg_ask_deneene_prompt( $question ) {
	$cards = sg_ask_deneene_select( $question );
	$body  = array();
	foreach ( $cards as $card ) {
		$body[] = sg_ask_deneene_format_card( $card );
	}
	$ql          = strtolower( (string) $question );
	$event_hints = array( 'today', 'tomorrow', 'tonight', 'happening', 'event', 'calendar', 'this week', 'weekend', 'meditation', 'educational', 'reiki share', 'fair', 'besom', 'who is in', "who's in", 'open today', 'schedule' );
	$want        = ( $ql === '' );
	foreach ( $event_hints as $h ) {
		if ( strpos( $ql, $h ) !== false ) {
			$want = true;
			break;
		}
	}
	$live = $want ? "\n\n" . sg_ask_deneene_events() : '';
	return "You are the Ask Deneene box on the live Sacred Ground website. "
		. "Not a private session or a reading.\n"
		. "Speak in Deneene's house voice: warm, plain, curious, practical. "
		. "Inspired by Deneene Florino, who founded this place. "
		. "If they ask whether they are talking to Deneene in the room, use SG-VOICE-IDENTITY. "
		. "Do not invent her memories, her sessions, or private stories.\n"
		. "Answer ONLY from the cards below and the live calendar slice when it is present. "
		. "Prefer the spoken line. "
		. "If they ask for a person's page, booking, or a link, the chat may show a pressable button from the card. "
		. "Never invent a URL. Never speak, spell, or read a website or /book/ path out loud. "
		. "The spoken line still names the nav. "
		. "Desktop nav: Calendar, Shop, Observatory, Holistic Center, Monthly, Library, Contact. "
		. "A named person is Holistic Center, then Practitioners, then their name. "
		. "Events are Calendar. The newsletter is Monthly.\n"
		. "Do not default to “call the store” when a card already has the answer.\n"
		. "If they ask for a tarot card Sacred Ground does not display, do not name it. "
		. "Say it is not a card we use here, and offer another card or Observatory in the menu.\n"
		. "Never mention Tam, Tom Tewell, or BJ. BJ is not a practitioner right now.\n"
		. "Leave membership, Inner Circle, and Member Shop out. "
		. "The menu item is Monthly. Call it Monthly, not the newsletter.\n"
		. "We are not doctors and we do not give medical advice. "
		. "Say that only when they ask about health, symptoms, diagnosis, medication, or whether a session, stone, or card will treat something. "
		. "Do not add it to ordinary shop, calendar, or menu questions.\n"
		. "Do not invent hours, prices, stock, or a time that is not on a booking page. "
		. "Do not say you booked, charged, registered, or shipped anything.\n"
		. "Address is always 160 West Campbell Street, Arlington Heights, IL 60005. Say West, never W. "
		. "Phone 847-749-3922. Working Calendar is staff only — never send a visitor there.\n"
		. "If the cards do not cover it, say so and name the closest menu item, or the phone.\n\n"
		. implode( "\n\n", $body )
		. $live;
}

/**
 * @return string
 */
function sg_ask_deneene_openrouter_key() {
	foreach ( array( 'ml_openrouter_key', 'ml_override_openrouter', 'ml_image_editor_openrouter_api_key' ) as $name ) {
		$val = get_option( $name, '' );
		if ( is_string( $val ) && $val !== '' ) {
			return $val;
		}
	}
	return '';
}

/**
 * @param string $bucket Bucket.
 * @param int    $limit  Hits.
 * @param int    $window Seconds.
 * @return bool
 */
function sg_ask_deneene_rate_ok( $bucket, $limit, $window ) {
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? (string) $_SERVER['REMOTE_ADDR'] : '0';
	$key = 'sg_ask_deneene_' . $bucket . '_' . md5( $ip );
	$n   = (int) get_transient( $key );
	if ( $n >= $limit ) {
		return false;
	}
	set_transient( $key, $n + 1, $window );
	return true;
}

/**
 * @param WP_REST_Request $request Request.
 * @return WP_REST_Response|WP_Error
 */
function sg_ask_deneene_rest_chat( $request ) {
	if ( ! sg_ask_deneene_rate_ok( 'chat', 30, 15 * MINUTE_IN_SECONDS ) ) {
		return new WP_Error( 'sg_ask_deneene_rate', 'Please wait a moment and try again.', array( 'status' => 429 ) );
	}
	$messages = $request->get_param( 'messages' );
	if ( ! is_array( $messages ) ) {
		$messages = array();
	}
	$question = '';
	$clean    = array();
	foreach ( array_slice( $messages, -8 ) as $row ) {
		if ( ! is_array( $row ) ) {
			continue;
		}
		$role = ( $row['role'] ?? '' ) === 'assistant' ? 'assistant' : 'user';
		$text = trim( wp_strip_all_tags( (string) ( $row['content'] ?? '' ) ) );
		if ( $text === '' ) {
			continue;
		}
		if ( strlen( $text ) > 800 ) {
			$text = substr( $text, 0, 800 );
		}
		$clean[] = array(
			'role'    => $role,
			'content' => $text,
		);
		if ( $role === 'user' ) {
			$question = $text;
		}
	}
	if ( $question === '' ) {
		return rest_ensure_response( array( 'reply' => 'Ask me anything about the shop, the calendar, or who can help you.' ) );
	}

	$key = sg_ask_deneene_openrouter_key();
	if ( $key === '' ) {
		return rest_ensure_response( array( 'reply' => 'The box could not answer just now. Try Calendar in the menu, or call 847-749-3922.' ) );
	}

	$payload = array(
		'model'       => SG_ASK_DENEENE_MODEL,
		'temperature' => 0.4,
		'messages'    => array_merge(
			array(
				array(
					'role'    => 'system',
					'content' => sg_ask_deneene_prompt( $question ),
				),
			),
			$clean
		),
	);

	$res = wp_remote_post(
		'https://openrouter.ai/api/v1/chat/completions',
		array(
			'timeout' => 45,
			'headers' => array(
				'Authorization' => 'Bearer ' . $key,
				'Content-Type'  => 'application/json',
				'HTTP-Referer'  => 'https://shopsacredground.com/',
				'X-Title'       => 'Sacred Ground Ask Deneene',
			),
			'body'    => wp_json_encode( $payload ),
		)
	);
	if ( is_wp_error( $res ) ) {
		return rest_ensure_response( array( 'reply' => 'The box could not answer just now. Try Calendar in the menu, or call 847-749-3922.' ) );
	}
	$code = (int) wp_remote_retrieve_response_code( $res );
	$body = json_decode( (string) wp_remote_retrieve_body( $res ), true );
	$text = '';
	if ( $code >= 200 && $code < 300 && is_array( $body ) ) {
		$text = trim( (string) ( $body['choices'][0]['message']['content'] ?? '' ) );
	}
	if ( $text === '' ) {
		return rest_ensure_response( array( 'reply' => 'The box could not answer just now. Try Calendar in the menu, or call 847-749-3922.' ) );
	}
	return rest_ensure_response(
		array(
			'reply' => $text,
			'links' => sg_ask_deneene_pressable_links( $question ),
		)
	);
}

/**
 * @param WP_REST_Request $request Request.
 * @return WP_REST_Response|WP_Error
 */
function sg_ask_deneene_rest_speak( $request ) {
	if ( ! sg_ask_deneene_rate_ok( 'speak', 40, 15 * MINUTE_IN_SECONDS ) ) {
		return new WP_Error( 'sg_ask_deneene_rate', 'Please wait a moment and try again.', array( 'status' => 429 ) );
	}
	$text = trim( wp_strip_all_tags( (string) $request->get_param( 'text' ) ) );
	$text = preg_replace( '/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/', '$1', $text );
	$text = preg_replace( '#https?://\S+#', '', $text );
	$text = preg_replace( '/\b160\s+W\.?\s+Campbell\b/i', '160 West Campbell', $text );
	$text = trim( preg_replace( '/\s+/', ' ', (string) $text ) );
	if ( $text === '' ) {
		return new WP_Error( 'sg_ask_deneene_empty', 'Nothing to speak.', array( 'status' => 400 ) );
	}
	if ( strlen( $text ) > 1200 ) {
		$text = substr( $text, 0, 1200 );
	}

	$voice = (string) get_option( 'mlprs_deneene_voice_id', '' );
	if ( $voice === '' ) {
		$voice = (string) get_option( 'mlprs_elevenlabs_voice_id', '' );
	}
	if ( $voice === '' ) {
		$voice = SG_ASK_DENEENE_VOICE_FALLBACK;
	}

	$uploads = wp_upload_dir();
	$dir     = trailingslashit( $uploads['basedir'] ) . 'sg-ask-deneene';
	if ( ! is_dir( $dir ) ) {
		wp_mkdir_p( $dir );
	}
	$hash = md5( $voice . '|' . $text );
	$file = $dir . '/' . $hash . '.mp3';
	$url  = trailingslashit( $uploads['baseurl'] ) . 'sg-ask-deneene/' . $hash . '.mp3';
	if ( is_readable( $file ) && filesize( $file ) > 200 ) {
		return rest_ensure_response( array( 'url' => $url ) );
	}

	$key = (string) get_option( 'mlprs_elevenlabs_key', '' );
	if ( $key === '' ) {
		return new WP_Error( 'sg_ask_deneene_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}

	$res = wp_remote_post(
		'https://api.elevenlabs.io/v1/text-to-speech/' . rawurlencode( $voice ),
		array(
			'timeout' => 45,
			'headers' => array(
				'xi-api-key'   => $key,
				'Content-Type' => 'application/json',
				'Accept'       => 'audio/mpeg',
			),
			'body'    => wp_json_encode(
				array(
					'text'     => $text,
					'model_id' => 'eleven_multilingual_v2',
				)
			),
		)
	);
	if ( is_wp_error( $res ) ) {
		return new WP_Error( 'sg_ask_deneene_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}
	$code = (int) wp_remote_retrieve_response_code( $res );
	$bin  = (string) wp_remote_retrieve_body( $res );
	if ( $code < 200 || $code >= 300 || strlen( $bin ) < 200 ) {
		return new WP_Error( 'sg_ask_deneene_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}
	file_put_contents( $file, $bin );
	return rest_ensure_response( array( 'url' => $url ) );
}

/**
 * Register chat + speak.
 *
 * @return void
 */
function sg_ask_deneene_routes() {
	register_rest_route(
		'sg-helper/v1',
		'/ask-deneene/chat',
		array(
			'methods'             => 'POST',
			'callback'            => 'sg_ask_deneene_rest_chat',
			'permission_callback' => '__return_true',
		)
	);
	register_rest_route(
		'sg-helper/v1',
		'/ask-deneene/speak',
		array(
			'methods'             => 'POST',
			'callback'            => 'sg_ask_deneene_rest_speak',
			'permission_callback' => '__return_true',
		)
	);
}
add_action( 'rest_api_init', 'sg_ask_deneene_routes' );

/**
 * Print the bubble on allowed public pages.
 *
 * @return void
 */
function sg_ask_deneene_footer() {
	if ( ! sg_ask_deneene_should_show() ) {
		return;
	}

	$photo  = esc_url( SG_ASK_DENEENE_PHOTO );
	$chat   = esc_url( rest_url( 'sg-helper/v1/ask-deneene/chat' ) );
	$speak  = esc_url( rest_url( 'sg-helper/v1/ask-deneene/speak' ) );
	$nonce  = wp_create_nonce( 'wp_rest' );
	$opener = 'Hi, I’m Deneene — the owner of Sacred Ground. Ask me anything about the shop, the calendar, or who can help you.';
	$top    = is_admin_bar_showing() ? '232px' : '200px';
	?>
<style id="sg-ask-deneene-css">
#sg-ask-deneene-open{position:fixed;left:20px;right:auto;top:<?php echo esc_attr( $top ); ?>;bottom:auto;display:flex;align-items:center;gap:6px;border:0;padding:4px 10px 4px 4px;background:#fff;border-radius:999px;box-shadow:0 10px 28px rgba(40,20,10,.22);cursor:pointer;z-index:99940;text-align:left;font:inherit;color:#1a1410;}
#sg-ask-deneene-open img{width:38px;height:38px;border-radius:50%;object-fit:cover;object-position:center;}
#sg-ask-deneene-open strong{display:block;font-size:12px;line-height:1.15;}
#sg-ask-deneene-open span{font-size:9px;color:#6a5648;}
#sg-ask-deneene-hero-slot{display:flex;justify-content:flex-start;margin-top:14px;max-width:100%;}
.sg-hero #sg-ask-deneene-open{position:static;left:auto;top:auto;right:auto;bottom:auto;z-index:3;margin:0;}
#sg-ask-deneene-back{display:none;position:fixed;inset:0;background:rgba(20,12,8,.45);align-items:center;justify-content:flex-start;padding:16px;z-index:99950;}
#sg-ask-deneene-back.open{display:flex;}
#sg-ask-deneene-box{width:min(360px,calc(100vw - 32px));height:min(46vh,380px);max-height:calc(100vh - 48px);min-height:0;background:#fff;border-radius:18px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 50px rgba(0,0,0,.28);font-family:"Avenir Next","Avenir","Helvetica Neue",sans-serif;color:#1a1410;}
#sg-ask-deneene-box .sg-top{position:relative;background:#efe6d8;display:flex;justify-content:center;padding:8px 12px 4px;flex-shrink:0;}
#sg-ask-deneene-box .sg-top img{width:64px;height:64px;border-radius:50%;object-fit:contain;object-position:center;display:block;background:#efe6d8;}
#sg-ask-deneene-box .sg-x{position:absolute;top:6px;right:6px;border:0;background:rgba(255,255,255,.92);width:28px;height:28px;border-radius:50%;font-size:18px;cursor:pointer;}
#sg-ask-deneene-box .sg-who{padding:4px 12px 2px;flex-shrink:0;}
#sg-ask-deneene-box .sg-who strong{display:block;font-size:16px;}
#sg-ask-deneene-box .sg-who em{font-style:normal;color:#6a5648;font-size:12px;}
#sg-ask-deneene-log{flex:1 1 auto;min-height:0;overflow-x:hidden;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:6px 12px 8px;display:flex;flex-direction:column;gap:8px;}
#sg-ask-deneene-log .sg-b{max-width:88%;padding:8px 10px;border-radius:12px;line-height:1.35;font-size:14px;}
#sg-ask-deneene-log .them{background:#efe6d8;align-self:flex-start;}
#sg-ask-deneene-log .me{background:#4a2c5a;color:#fff;align-self:flex-end;}
#sg-ask-deneene-form{display:flex;gap:8px;padding:8px 12px 12px;border-top:1px solid #eadfce;flex-shrink:0;}
#sg-ask-deneene-form input{flex:1;border:1px solid #d5c6b2;border-radius:12px;padding:8px 10px;font:inherit;font-size:14px;}
#sg-ask-deneene-form button{border:0;border-radius:12px;background:#4a2c5a;color:#fff;padding:8px 12px;font:inherit;font-size:14px;cursor:pointer;}
#sg-ask-deneene-form button.mic{background:#ffc63f;color:#111;width:40px;height:40px;padding:0;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
#sg-ask-deneene-form button.mic.on{background:#f8c038;box-shadow:0 0 0 3px rgba(255,198,63,.45);}
#sg-ask-deneene-form button.mic svg{display:block;}
#sg-ask-deneene-log .hear{margin-top:8px;}
#sg-ask-deneene-log .hear span{display:block;font-size:13px;color:#6a5648;margin-bottom:4px;}
#sg-ask-deneene-log .hear audio{width:100%;height:36px;}
#sg-ask-deneene-log .sg-b a{color:#4a2c5a;font-weight:600;word-break:break-word;}
#sg-ask-deneene-log .sg-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;}
#sg-ask-deneene-log .sg-links a{display:inline-block;background:#ffc63f;color:#111;text-decoration:none;border-radius:12px;padding:6px 10px;font-weight:600;font-size:13px;}
</style>
<button id="sg-ask-deneene-open" type="button">
  <img src="<?php echo $photo; ?>" alt=""/>
  <div><strong>Chat with Deneene</strong><span>Ask a question</span></div>
</button>
<div id="sg-ask-deneene-back">
  <div id="sg-ask-deneene-box" role="dialog" aria-label="Chat with Deneene">
    <div class="sg-top">
      <img src="<?php echo $photo; ?>" alt="Deneene"/>
      <button class="sg-x" id="sg-ask-deneene-close" type="button" aria-label="Close">×</button>
    </div>
    <div class="sg-who"><strong>Chat with Deneene</strong><em>Ask about the shop, the calendar, or who can help you.</em></div>
    <div id="sg-ask-deneene-log"></div>
    <form id="sg-ask-deneene-form"><input id="sg-ask-deneene-q" type="text" placeholder="Ask a question…" autocomplete="off"/><button type="button" class="mic" id="sg-ask-deneene-mic" aria-label="Use microphone" title="Use microphone"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg></button><button type="submit">Send</button></form>
  </div>
</div>
<script>
(function(){
  var CHAT=<?php echo wp_json_encode( $chat ); ?>;
  var SPEAK=<?php echo wp_json_encode( $speak ); ?>;
  var NONCE=<?php echo wp_json_encode( $nonce ); ?>;
  var OPENER=<?php echo wp_json_encode( $opener ); ?>;
  var log=document.getElementById("sg-ask-deneene-log");
  var q=document.getElementById("sg-ask-deneene-q");
  var history=[];
  var primed=false;
  function attachVoice(audio,text){
    fetch(SPEAK,{method:"POST",headers:{"Content-Type":"application/json","X-WP-Nonce":NONCE},body:JSON.stringify({text:text})})
      .then(function(r){return r.ok?r.json():null;})
      .then(function(d){if(d&&d.url) audio.src=d.url;});
  }
  function speakText(t){
    return String(t||"").replace(/\[[^\]]+\]\((https?:\/\/[^)]+)\)/g," ").replace(/https?:\/\/\S+/g," ").replace(/\s+/g," ").trim();
  }
  function add(t,w,voice,links){
    var d=document.createElement("div"); d.className="sg-b "+w;
    var p=document.createElement("div"); p.textContent=t; d.appendChild(p);
    if(w==="them" && links && links.length){
      var row=document.createElement("div"); row.className="sg-links";
      links.forEach(function(L){
        if(!L||!L.url||String(L.url).indexOf("https://shopsacredground.com/")!==0) return;
        var a=document.createElement("a"); a.href=L.url; a.textContent=L.label||"Open this page";
        row.appendChild(a);
      });
      if(row.childNodes.length) d.appendChild(row);
    }
    if(w==="them"){
      var wrap=document.createElement("div"); wrap.className="hear";
      var note=document.createElement("span"); note.textContent="Press Play to hear me";
      var audio=document.createElement("audio"); audio.preload="none"; audio.controls=true; audio.setAttribute("playsinline","");
      wrap.appendChild(note); wrap.appendChild(audio); d.appendChild(wrap);
      var spoken=speakText(t);
      if(voice===false) audio.dataset.text=spoken; else attachVoice(audio,spoken);
    }
    log.appendChild(d); log.scrollTop=log.scrollHeight;
  }
  add(OPENER,"them",false);
  document.getElementById("sg-ask-deneene-open").onclick=function(){
    document.getElementById("sg-ask-deneene-back").classList.add("open"); q.focus();
    if(!primed){ primed=true; var a=log.querySelector("audio"); if(a&&a.dataset.text) attachVoice(a,a.dataset.text); }
  };
  (function(){
    var btns=document.querySelector(".sg-hero-btns");
    var open=document.getElementById("sg-ask-deneene-open");
    if(!btns||!open) return;
    var slot=document.createElement("div");
    slot.id="sg-ask-deneene-hero-slot";
    btns.insertAdjacentElement("afterend",slot);
    slot.appendChild(open);
  })();
  (function(){
    var open=document.getElementById("sg-ask-deneene-open");
    if(!open || open.closest(".sg-hero")) return;
    function place(){
      var bottom=0;
      var nodes=document.querySelectorAll("#wpadminbar, #sg-fair-static, .sg-fair-static, #masthead, header.site-header");
      for(var i=0;i<nodes.length;i++){
        var r=nodes[i].getBoundingClientRect();
        if(r.bottom>bottom) bottom=r.bottom;
      }
      if(bottom<80) bottom=188;
      open.style.top=Math.round(bottom+12)+"px";
    }
    place();
    window.addEventListener("resize", place);
  })();
  document.getElementById("sg-ask-deneene-close").onclick=function(){ document.getElementById("sg-ask-deneene-back").classList.remove("open"); };
  document.getElementById("sg-ask-deneene-back").addEventListener("click",function(e){ if(e.target.id==="sg-ask-deneene-back") e.currentTarget.classList.remove("open"); });
  (function(){
    var btn=document.getElementById("sg-ask-deneene-mic");
    var form=document.getElementById("sg-ask-deneene-form");
    if(!btn||!form) return;
    var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    var rec=null, on=false;
    function off(){ on=false; btn.classList.remove("on"); btn.setAttribute("aria-pressed","false"); try{ if(rec) rec.stop(); }catch(err){} }
    function send(){
      var t=(q.value||"").trim(); if(!t) return;
      try{ if(form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit",{cancelable:true,bubbles:true})); }catch(err){}
    }
    btn.addEventListener("click", function(ev){
      ev.preventDefault();
      if(!SR){ q.placeholder="Type your question — this browser can't hear you"; q.focus(); return; }
      if(on){ off(); return; }
      try{
        rec=new SR(); rec.lang="en-US"; rec.interimResults=true; rec.continuous=false;
        rec.onresult=function(e){
          try{
            var t=""; for(var i=0;i<e.results.length;i++) t+=e.results[i][0].transcript;
            q.value=t;
            if(e.results[e.results.length-1].isFinal){ off(); send(); }
          }catch(err){ off(); }
        };
        rec.onend=function(){ on=false; btn.classList.remove("on"); };
        rec.onerror=function(){ off(); };
        on=true; btn.classList.add("on"); btn.setAttribute("aria-pressed","true");
        rec.start();
      }catch(err){ off(); q.placeholder="Type your question — the mic didn't start"; q.focus(); }
    });
  })();
  document.getElementById("sg-ask-deneene-form").onsubmit=async function(e){
    e.preventDefault(); var text=q.value.trim(); if(!text) return; q.value=""; add(text,"me"); history.push({role:"user",content:text});
    var thinking=document.createElement("div"); thinking.className="sg-b them"; thinking.textContent="…"; log.appendChild(thinking);
    try {
      var res=await fetch(CHAT,{method:"POST",headers:{"Content-Type":"application/json","X-WP-Nonce":NONCE},body:JSON.stringify({messages:history})});
      var data=await res.json(); thinking.remove();
      var reply=(data&&data.reply)||(data&&data.message)||"The box did not answer.";
      add(reply,"them",true,data&&data.links); history.push({role:"assistant",content:reply});
    } catch(err) { thinking.remove(); add("The box could not answer just now.","them"); }
  };
})();
</script>
	<?php
}
add_action( 'wp_footer', 'sg_ask_deneene_footer', 40 );
