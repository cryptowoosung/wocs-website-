<?php
/*
Plugin Name: WOCS Auto Importer
Description: GitHub content 폴더에서 블로그 글을 가져와 자동 포스팅
Version: 2.0
Author: WOCS
*/
defined('ABSPATH') || exit;

// 메뉴 등록
add_action('admin_menu', function() {
    add_submenu_page('tools.php', 'WOCS 임포터', 'WOCS 임포터', 'manage_options', 'wocs-importer', 'wocs_importer_page');
});

// 페이지 렌더링
function wocs_importer_page() {
    echo '<div class="wrap"><h1>WOCS Auto Importer v2.0</h1>';

    if (isset($_POST['wocs_go']) && wp_verify_nonce($_POST['_wpnonce'], 'wocs_go')) {
        wocs_do_import();
    }

    echo '<form method="post">';
    wp_nonce_field('wocs_go');
    echo '<p><button type="submit" name="wocs_go" value="1" class="button button-primary">지금 실행</button></p>';
    echo '</form></div>';
}

// 임포트 실행
function wocs_do_import() {
    $today = date('Y-m-d');
    $base  = 'https://raw.githubusercontent.com/cryptowoosung/wocs-website-/main/content/';
    $api   = 'https://api.github.com/repos/cryptowoosung/wocs-website-/contents/content';

    echo '<h2>실행 결과</h2><pre>';

    // 파일 목록 가져오기
    $res = wp_remote_get($api, array('timeout' => 30, 'headers' => array('User-Agent' => 'WOCS/2.0')));
    if (is_wp_error($res)) {
        echo 'GitHub API 오류: ' . esc_html($res->get_error_message());
        echo '</pre>'; return;
    }

    $files = json_decode(wp_remote_retrieve_body($res), true);
    if (!is_array($files)) {
        echo 'GitHub 응답 파싱 실패 (HTTP ' . wp_remote_retrieve_response_code($res) . ')';
        echo '</pre>'; return;
    }

    // 오늘 날짜 파일 필터
    $targets = array();
    foreach ($files as $f) {
        if (isset($f['name']) && strpos($f['name'], 'auto_post_' . $today) === 0) {
            $targets[] = $f['name'];
        }
    }

    if (empty($targets)) {
        echo "오늘($today) 파일 없음. 전체 최신 파일 시도...\n";
        foreach ($files as $f) {
            if (isset($f['name']) && strpos($f['name'], 'auto_post_') === 0) {
                $targets[] = $f['name'];
            }
        }
        rsort($targets);
        $targets = array_slice($targets, 0, 1);
    }

    if (empty($targets)) {
        echo 'auto_post 파일이 없습니다.';
        echo '</pre>'; return;
    }

    foreach ($targets as $fname) {
        echo "\n파일: $fname\n";

        // 중복 확인
        $dup = get_posts(array('meta_key' => '_wocs_src', 'meta_value' => $fname, 'post_type' => 'post', 'numberposts' => 1));
        if ($dup) {
            echo "  이미 등록됨 (ID: {$dup[0]->ID}), 건너뜀\n";
            continue;
        }

        // 파일 다운로드
        $dl = wp_remote_get($base . $fname, array('timeout' => 30, 'headers' => array('User-Agent' => 'WOCS/2.0')));
        if (is_wp_error($dl)) {
            echo '  다운로드 실패: ' . esc_html($dl->get_error_message()) . "\n";
            continue;
        }

        $lines = explode("\n", wp_remote_retrieve_body($dl));
        if (count($lines) < 5) {
            echo "  파일 형식 오류\n";
            continue;
        }

        $title = sanitize_text_field($lines[0]);
        $pdate = sanitize_text_field($lines[1]);
        $body  = implode("\n", array_slice($lines, 4));
        $body  = wpautop(esc_html($body));
        $body .= '<hr><p><strong>WOCS</strong> | <a href="https://wocs.kr">wocs.kr</a> | <a href="tel:01043370582">010-4337-0582</a></p>';

        $pid = wp_insert_post(array(
            'post_title'   => $title,
            'post_content' => $body,
            'post_status'  => 'publish',
            'post_date'    => $pdate . ' 09:00:00',
        ), true);

        if (is_wp_error($pid)) {
            echo '  등록 실패: ' . esc_html($pid->get_error_message()) . "\n";
        } else {
            update_post_meta($pid, '_wocs_src', $fname);
            echo "  등록 완료! ID: $pid\n";
            echo '  URL: ' . get_permalink($pid) . "\n";
        }
    }

    echo '</pre>';
}
