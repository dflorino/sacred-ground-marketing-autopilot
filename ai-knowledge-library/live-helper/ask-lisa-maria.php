<?php
/**
 * Chat with Lisa Maria — her practitioner page only.
 *
 * Same placement and size as Ask Deneene. Her face. Stem 2 voice.
 * Never uses Deneene's locked voice.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'SG_ASK_LISA_MARIA_VOICE', '21m00Tcm4TlvDq8ikWAM' );
define( 'SG_ASK_LISA_MARIA_PHOTO', 'https://shopsacredground.com/wp-content/uploads/239415714409977658.jpg' );
define( 'SG_ASK_LISA_MARIA_MODEL', 'openai/gpt-4.1-mini' );
define( 'SG_ASK_LISA_MARIA_SLUG', 'lisa-maria-11' );

/**
 * @return bool
 */
function sg_ask_lisa_maria_should_show() {
	if ( is_admin() || wp_doing_ajax() || wp_doing_cron() || is_feed() ) {
		return false;
	}
	if ( function_exists( 'wp_is_json_request' ) && wp_is_json_request() ) {
		return false;
	}

	$slug = '';
	$obj  = get_queried_object();
	if ( $obj && ! empty( $obj->post_name ) ) {
		$slug = strtolower( (string) $obj->post_name );
	} else {
		$path = (string) parse_url( isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '', PHP_URL_PATH );
		$bits = explode( '/', trim( $path, '/' ) );
		$slug = strtolower( (string) end( $bits ) );
	}

	return $slug === SG_ASK_LISA_MARIA_SLUG;
}

/**
 * @param int $user_turns How many visitor questions are already in the thread.
 * @return string
 */
function sg_ask_lisa_maria_prompt( $user_turns = 0 ) {
	$booking = ( (int) $user_turns < 2 )
		? "They just started chatting. Answer the question they asked. Do not mention booking, finding a time, or the Book a time button yet.\n"
		: "You have talked a little. You may now say they can book a time with you. One short humble line. Point them to the Book a time button. Do not sound salesy.\n";
	return "You are Lisa Maria's talking box on her Sacred Ground practitioner page only.\n"
		. "Speak as Lisa Maria. Humble. Warm. Inviting. Not a performance.\n"
		. "The first hello is already on the screen. Never repeat it. "
		. "Never start again with Hi I'm Lisa Maria, I do tarot, let's find a time, or let's chat.\n"
		. "Answer the question they just asked.\n"
		. $booking
		. "Never say you are not here for small talk. Never sound curt or dismissive.\n"
		. "This is NOT the live reading. Do not pull cards. Do not invent a spread, a future, hours, or a price.\n"
		. "Do not read a website. Do not give email, PayPal, Venmo, Cash App, or a price.\n"
		. "Not Lisa the astrologer. Not Lisa Seyring.\n"
		. "I am an artist and teacher for more than twenty years. Intuitive tarot and oracle, about eight decks, "
		. "crystals, astrology in the mix. I read energy and talk with angels and guides. "
		. "The session is a conversation. Kind. People leave feeling heard.\n"
		. "Somatic / biofield / tuning-fork work is energy and sound, not medicine. "
		. "We are not doctors. Say that only if they ask whether a session treats a symptom or a diagnosis.\n"
		. "If no time is open, say so and offer 847-749-3922.\n"
		. "Address is 160 West Campbell Street, Arlington Heights, IL 60005. Say West, never W.\n";
}

/**
 * @return string
 */
function sg_ask_lisa_maria_openrouter_key() {
	if ( function_exists( 'sg_ask_deneene_openrouter_key' ) ) {
		return sg_ask_deneene_openrouter_key();
	}
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
function sg_ask_lisa_maria_rate_ok( $bucket, $limit, $window ) {
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? (string) $_SERVER['REMOTE_ADDR'] : '0';
	$key = 'sg_ask_lisa_maria_' . $bucket . '_' . md5( $ip );
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
function sg_ask_lisa_maria_rest_chat( $request ) {
	if ( ! sg_ask_lisa_maria_rate_ok( 'chat', 30, 15 * MINUTE_IN_SECONDS ) ) {
		return new WP_Error( 'sg_ask_lisa_maria_rate', 'Please wait a moment and try again.', array( 'status' => 429 ) );
	}
	$messages = $request->get_param( 'messages' );
	if ( ! is_array( $messages ) ) {
		$messages = array();
	}
	$question   = '';
	$clean      = array();
	$user_turns = 0;
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
			$user_turns++;
		}
	}
	if ( $question === '' ) {
		return rest_ensure_response( array( 'reply' => 'Ask me how a session feels. If you have questions, let\'s chat.' ) );
	}

	$key = sg_ask_lisa_maria_openrouter_key();
	if ( $key === '' ) {
		return rest_ensure_response( array( 'reply' => 'I could not answer just now. You can still book a time on this page, or call 847-749-3922.' ) );
	}

	$payload = array(
		'model'       => SG_ASK_LISA_MARIA_MODEL,
		'temperature' => 0.45,
		'messages'    => array_merge(
			array(
				array(
					'role'    => 'system',
					'content' => sg_ask_lisa_maria_prompt( $user_turns ),
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
				'X-Title'       => 'Sacred Ground Ask Lisa Maria',
			),
			'body'    => wp_json_encode( $payload ),
		)
	);
	if ( is_wp_error( $res ) ) {
		return rest_ensure_response( array( 'reply' => 'I could not answer just now. You can still book a time on this page, or call 847-749-3922.' ) );
	}
	$code = (int) wp_remote_retrieve_response_code( $res );
	$body = json_decode( (string) wp_remote_retrieve_body( $res ), true );
	$text = '';
	if ( $code >= 200 && $code < 300 && is_array( $body ) ) {
		$text = trim( (string) ( $body['choices'][0]['message']['content'] ?? '' ) );
	}
	if ( $text === '' ) {
		return rest_ensure_response( array( 'reply' => 'I could not answer just now. You can still book a time on this page, or call 847-749-3922.' ) );
	}
	return rest_ensure_response( array( 'reply' => sg_ask_lisa_maria_drop_hello( $text, $question ) ) );
}

/**
 * @param string $text     Reply.
 * @param string $question User text.
 * @return string
 */
function sg_ask_lisa_maria_drop_hello( $text, $question ) {
	if ( $question === '' ) {
		return $text;
	}
	$low = strtolower( $text );
	if ( strpos( $low, "hi, i'm lisa maria" ) !== 0 && strpos( $low, "hi i'm lisa maria" ) !== 0 ) {
		return $text;
	}
	$parts = preg_split( '/(?<=[.!?])\s+/', $text );
	$kept  = array();
	$skip  = true;
	foreach ( $parts as $part ) {
		$bit = trim( $part );
		if ( $bit === '' ) {
			continue;
		}
		$check = strtolower( $bit );
		if ( $skip && ( strpos( $check, "i'm lisa maria" ) !== false || strpos( $check, 'i do tarot' ) !== false || strpos( $check, "let's find a time" ) !== false || strpos( $check, "let's chat" ) !== false ) ) {
			continue;
		}
		$skip   = false;
		$kept[] = $bit;
	}
	$out = trim( implode( ' ', $kept ) );
	return $out !== '' ? $out : $text;
}

/**
 * @param WP_REST_Request $request Request.
 * @return WP_REST_Response|WP_Error
 */
function sg_ask_lisa_maria_rest_speak( $request ) {
	if ( ! sg_ask_lisa_maria_rate_ok( 'speak', 40, 15 * MINUTE_IN_SECONDS ) ) {
		return new WP_Error( 'sg_ask_lisa_maria_rate', 'Please wait a moment and try again.', array( 'status' => 429 ) );
	}
	$text = trim( wp_strip_all_tags( (string) $request->get_param( 'text' ) ) );
	$text = preg_replace( '/\b160\s+W\.?\s+Campbell\b/i', '160 West Campbell', $text );
	if ( $text === '' ) {
		return new WP_Error( 'sg_ask_lisa_maria_empty', 'Nothing to speak.', array( 'status' => 400 ) );
	}
	if ( strlen( $text ) > 1200 ) {
		$text = substr( $text, 0, 1200 );
	}

	$voice   = SG_ASK_LISA_MARIA_VOICE;
	$uploads = wp_upload_dir();
	$dir     = trailingslashit( $uploads['basedir'] ) . 'sg-ask-lisa-maria';
	if ( ! is_dir( $dir ) ) {
		wp_mkdir_p( $dir );
	}
	$hash = md5( $voice . '|0.88|' . $text );
	$file = $dir . '/' . $hash . '.mp3';
	$url  = trailingslashit( $uploads['baseurl'] ) . 'sg-ask-lisa-maria/' . $hash . '.mp3';
	if ( is_readable( $file ) && filesize( $file ) > 200 ) {
		return rest_ensure_response( array( 'url' => $url ) );
	}

	$key = (string) get_option( 'mlprs_elevenlabs_key', '' );
	if ( $key === '' ) {
		return new WP_Error( 'sg_ask_lisa_maria_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}

	$res = wp_remote_post(
		'https://api.elevenlabs.io/v1/text-to-speech/' . rawurlencode( $voice ),
		array(
			'timeout' => 45,
			'headers' => array(
				'xi-api-key'   => $key,
				'Accept'       => 'audio/mpeg',
				'Content-Type' => 'application/json',
			),
			'body'    => wp_json_encode(
				array(
					'text'            => $text,
					'model_id'        => 'eleven_multilingual_v2',
					'voice_settings'  => array(
						'stability'        => 0.52,
						'similarity_boost' => 0.78,
						'style'            => 0.12,
						'speed'            => 0.88,
					),
				)
			),
		)
	);
	if ( is_wp_error( $res ) ) {
		return new WP_Error( 'sg_ask_lisa_maria_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}
	$code  = (int) wp_remote_retrieve_response_code( $res );
	$audio = (string) wp_remote_retrieve_body( $res );
	if ( $code < 200 || $code >= 300 || strlen( $audio ) < 200 ) {
		return new WP_Error( 'sg_ask_lisa_maria_voice', 'Voice is not ready.', array( 'status' => 503 ) );
	}
	file_put_contents( $file, $audio );
	return rest_ensure_response( array( 'url' => $url ) );
}

/**
 * @return void
 */
function sg_ask_lisa_maria_routes() {
	register_rest_route(
		'sg-helper/v1',
		'/ask-lisa-maria/chat',
		array(
			'methods'             => 'POST',
			'callback'            => 'sg_ask_lisa_maria_rest_chat',
			'permission_callback' => '__return_true',
		)
	);
	register_rest_route(
		'sg-helper/v1',
		'/ask-lisa-maria/speak',
		array(
			'methods'             => 'POST',
			'callback'            => 'sg_ask_lisa_maria_rest_speak',
			'permission_callback' => '__return_true',
		)
	);
}
add_action( 'rest_api_init', 'sg_ask_lisa_maria_routes' );

/**
 * @return void
 */
function sg_ask_lisa_maria_footer() {
	if ( ! sg_ask_lisa_maria_should_show() ) {
		return;
	}

	$photo  = esc_url( SG_ASK_LISA_MARIA_PHOTO );
	$chat   = esc_url( rest_url( 'sg-helper/v1/ask-lisa-maria/chat' ) );
	$speak  = esc_url( rest_url( 'sg-helper/v1/ask-lisa-maria/speak' ) );
	$book   = esc_url( home_url( '/book/lisa-maria/' ) );
	$nonce  = wp_create_nonce( 'wp_rest' );
	$opener = "Hi, I'm Lisa Maria. I do tarot and somatic healing. If you have any questions for me, let's chat.";
	$top    = is_admin_bar_showing() ? '232px' : '200px';
	?>
<style id="sg-ask-lisa-maria-css">
#sg-ask-lisa-maria-open{position:fixed;left:20px;right:auto;top:<?php echo esc_attr( $top ); ?>;bottom:auto;display:flex;align-items:center;gap:6px;border:0;padding:4px 10px 4px 4px;background:#fff;border-radius:999px;box-shadow:0 10px 28px rgba(40,20,10,.22);cursor:pointer;z-index:99940;text-align:left;font:inherit;color:#1a1410;}
#sg-ask-lisa-maria-open img{width:38px;height:38px;border-radius:50%;object-fit:cover;object-position:center top;background:#efe6d8;}
#sg-ask-lisa-maria-open strong{display:block;font-size:12px;line-height:1.15;}
#sg-ask-lisa-maria-open span{font-size:9px;color:#6a5648;}
#sg-ask-lisa-maria-back{display:none;position:fixed;inset:0;background:rgba(20,12,8,.45);align-items:center;justify-content:flex-start;padding:16px;z-index:99950;}
#sg-ask-lisa-maria-back.open{display:flex;}
#sg-ask-lisa-maria-box{width:min(420px,calc(100vw - 32px));height:min(70vh,620px);max-height:calc(100vh - 32px);min-height:0;background:#fff;border-radius:18px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 50px rgba(0,0,0,.28);font-family:"Avenir Next","Avenir","Helvetica Neue",sans-serif;color:#1a1410;}
#sg-ask-lisa-maria-box .sg-top{position:relative;background:#efe6d8;display:flex;justify-content:center;padding:14px 16px 6px;flex-shrink:0;}
#sg-ask-lisa-maria-box .sg-top img{width:88px;height:88px;border-radius:50%;object-fit:cover;object-position:center top;display:block;background:#efe6d8;}
#sg-ask-lisa-maria-box .sg-x{position:absolute;top:10px;right:10px;border:0;background:rgba(255,255,255,.92);width:36px;height:36px;border-radius:50%;font-size:20px;cursor:pointer;}
#sg-ask-lisa-maria-box .sg-who{padding:8px 16px 6px;flex-shrink:0;}
#sg-ask-lisa-maria-box .sg-who strong{display:block;font-size:22px;}
#sg-ask-lisa-maria-box .sg-who em{font-style:normal;color:#6a5648;font-size:14px;}
#sg-ask-lisa-maria-log{flex:1 1 auto;min-height:0;overflow-x:hidden;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:8px 16px 12px;display:flex;flex-direction:column;gap:10px;}
#sg-ask-lisa-maria-log .sg-b{max-width:88%;padding:10px 12px;border-radius:14px;line-height:1.4;font-size:16px;}
#sg-ask-lisa-maria-log .them{background:#efe6d8;align-self:flex-start;}
#sg-ask-lisa-maria-log .me{background:#4a2c5a;color:#fff;align-self:flex-end;}
#sg-ask-lisa-maria-book{display:block;margin:0 16px 10px;text-align:center;text-decoration:none;border-radius:12px;background:#c4a35a;color:#1a1410;padding:10px 14px;font-weight:600;flex-shrink:0;}
#sg-ask-lisa-maria-form{display:flex;gap:8px;padding:12px 16px 16px;border-top:1px solid #eadfce;flex-shrink:0;}
#sg-ask-lisa-maria-form input{flex:1;border:1px solid #d5c6b2;border-radius:12px;padding:10px 12px;font:inherit;}
#sg-ask-lisa-maria-form button{border:0;border-radius:12px;background:#4a2c5a;color:#fff;padding:10px 14px;font:inherit;cursor:pointer;}
#sg-ask-lisa-maria-form button.mic{background:#efe6d8;color:#1a1410;}
#sg-ask-lisa-maria-form button.mic.on{background:#c4a35a;}
#sg-ask-lisa-maria-log .hear{margin-top:8px;}
#sg-ask-lisa-maria-log .hear span{display:block;font-size:13px;color:#6a5648;margin-bottom:4px;}
#sg-ask-lisa-maria-log .hear audio{width:100%;height:36px;}
</style>
<button id="sg-ask-lisa-maria-open" type="button">
  <img src="<?php echo $photo; ?>" alt="Lisa Maria"/>
  <div><strong>Chat with Lisa Maria</strong><span>Ask a question</span></div>
</button>
<div id="sg-ask-lisa-maria-back">
  <div id="sg-ask-lisa-maria-box" role="dialog" aria-label="Chat with Lisa Maria">
    <div class="sg-top">
      <img src="<?php echo $photo; ?>" alt="Lisa Maria"/>
      <button class="sg-x" id="sg-ask-lisa-maria-close" type="button" aria-label="Close">×</button>
    </div>
    <div class="sg-who"><strong>Chat with Lisa Maria</strong><em>Not the live reading. Ask how a session feels.</em></div>
    <div id="sg-ask-lisa-maria-log"></div>
    <a class="sg-book" id="sg-ask-lisa-maria-book" href="<?php echo $book; ?>">Book a time</a>
    <form id="sg-ask-lisa-maria-form"><input id="sg-ask-lisa-maria-q" type="text" placeholder="Type or speak a question…" autocomplete="off"/><button type="button" class="mic" id="sg-ask-lisa-maria-mic" aria-label="Speak">Speak</button><button type="submit">Send</button></form>
  </div>
</div>
<script>
(function(){
  var CHAT=<?php echo wp_json_encode( $chat ); ?>;
  var SPEAK=<?php echo wp_json_encode( $speak ); ?>;
  var NONCE=<?php echo wp_json_encode( $nonce ); ?>;
  var OPENER=<?php echo wp_json_encode( $opener ); ?>;
  var log=document.getElementById("sg-ask-lisa-maria-log");
  var q=document.getElementById("sg-ask-lisa-maria-q");
  var history=[{role:"assistant",content:OPENER}];
  var primed=false;
  function attachVoice(audio,text){
    fetch(SPEAK,{method:"POST",headers:{"Content-Type":"application/json","X-WP-Nonce":NONCE},body:JSON.stringify({text:text})})
      .then(function(r){return r.ok?r.json():null;})
      .then(function(d){if(d&&d.url) audio.src=d.url;});
  }
  function add(t,w,voice){
    var d=document.createElement("div"); d.className="sg-b "+w;
    var p=document.createElement("div"); p.textContent=t; d.appendChild(p);
    if(w==="them"){
      var wrap=document.createElement("div"); wrap.className="hear";
      var note=document.createElement("span"); note.textContent="Press Play to hear me";
      var audio=document.createElement("audio"); audio.preload="none"; audio.controls=true; audio.setAttribute("playsinline","");
      wrap.appendChild(note); wrap.appendChild(audio); d.appendChild(wrap);
      if(voice===false) audio.dataset.text=t; else attachVoice(audio,t);
    }
    log.appendChild(d); log.scrollTop=log.scrollHeight;
  }
  add(OPENER,"them",false);
  document.getElementById("sg-ask-lisa-maria-open").onclick=function(){
    document.getElementById("sg-ask-lisa-maria-back").classList.add("open"); q.focus();
    if(!primed){ primed=true; var a=log.querySelector("audio"); if(a&&a.dataset.text) attachVoice(a,a.dataset.text); }
  };
  (function(){
    var open=document.getElementById("sg-ask-lisa-maria-open");
    if(!open) return;
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
  document.getElementById("sg-ask-lisa-maria-close").onclick=function(){ document.getElementById("sg-ask-lisa-maria-back").classList.remove("open"); };
  document.getElementById("sg-ask-lisa-maria-back").addEventListener("click",function(e){ if(e.target.id==="sg-ask-lisa-maria-back") e.currentTarget.classList.remove("open"); });
  (function(){
    var btn=document.getElementById("sg-ask-lisa-maria-mic");
    var form=document.getElementById("sg-ask-lisa-maria-form");
    var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!SR||!btn){ if(btn) btn.hidden=true; return; }
    var rec=new SR(); rec.lang="en-US"; rec.interimResults=true; rec.continuous=false; var on=false;
    rec.onresult=function(e){
      var t=""; for(var i=0;i<e.results.length;i++) t+=e.results[i][0].transcript;
      q.value=t;
      if(e.results[e.results.length-1].isFinal){
        on=false; btn.classList.remove("on"); btn.setAttribute("aria-pressed","false");
        if(t.trim()){ if(form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit",{cancelable:true,bubbles:true})); }
      }
    };
    rec.onend=function(){ on=false; btn.classList.remove("on"); btn.setAttribute("aria-pressed","false"); };
    rec.onerror=function(){ on=false; btn.classList.remove("on"); btn.setAttribute("aria-pressed","false"); };
    btn.onclick=function(){
      if(on){ try{rec.stop();}catch(err){} return; }
      on=true; btn.classList.add("on"); btn.setAttribute("aria-pressed","true");
      try{rec.start();}catch(err){ on=false; btn.classList.remove("on"); }
    };
  })();
  document.getElementById("sg-ask-lisa-maria-form").onsubmit=async function(e){
    e.preventDefault(); var text=q.value.trim(); if(!text) return; q.value=""; add(text,"me"); history.push({role:"user",content:text});
    var thinking=document.createElement("div"); thinking.className="sg-b them"; thinking.textContent="…"; log.appendChild(thinking);
    try {
      var res=await fetch(CHAT,{method:"POST",headers:{"Content-Type":"application/json","X-WP-Nonce":NONCE},body:JSON.stringify({messages:history})});
      var data=await res.json(); thinking.remove();
      var reply=(data&&data.reply)||(data&&data.message)||"The box did not answer.";
      add(reply,"them"); history.push({role:"assistant",content:reply});
    } catch(err) { thinking.remove(); add("I could not answer just now.","them"); }
  };
})();
</script>
	<?php
}
if ( function_exists( 'sg_ask_lisa_maria_footer' ) ) {
	add_action( 'wp_footer', 'sg_ask_lisa_maria_footer', 41 );
}
