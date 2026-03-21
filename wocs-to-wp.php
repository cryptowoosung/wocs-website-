<?php
/*
Plugin Name: WOCS Auto Importer
Description: GitHub content 폴더에서 블로그 글을 가져와 자동 포스팅
Version: 2.0
Author: WOCS
*/
defined('ABSPATH') || exit;

add_action('admin_menu', function() {
    add_submenu_page('tools.php', 'WOCS 임포터', 'WOCS 임포터', 'manage_options', 'wocs-importer', 'wocs_importer_page');
});

function wocs_importer_page() {
    echo '<div class="wrap"><h1>WOCS 자동 임포터</h1>';
    if (isset($_POST['run']) && check_admin_referer('wocs_import')) {
        wocs_do_import();
    }
    echo '<form method="post">';
    wp_nonce_field('wocs_import');
    echo '<p><input type="submit" name="run" class="button button-primary" value="지금 실행"></p></form></div>';
}

function wocs_do_import() {
    $api = 'https://api.github.com/repos/cryptowoosung/wocs-website-/contents/content';
    $res = wp_remote_get($api, array('headers' => array('User-Agent' => 'WordPress')));
    if (is_wp_error($res)) { echo '<p>GitHub 연결 실패</p>'; return; }
    $files = json_decode(wp_remote_retrieve_body($res), true);
    if (!$files) { echo '<p>파일 없음</p>'; return; }
    $today = date('Y-m-d');
    $target = null;
    foreach ($files as $f) {
        if (strpos($f['name'], 'auto_post_' . $today) !== false) { $target = $f; break; }
    }
    if (!$target) $target = end($files);
    $exists = get_posts(array('meta_key' => '_wocs_src', 'meta_value' => $target['name'], 'post_type' => 'post', 'numberposts' => 1));
    if ($exists) { echo '<p>이미 등록된 글입니다.</p>'; return; }
    $body = wp_remote_retrieve_body(wp_remote_get($target['download_url']));
    $lines = explode("\n", $body);
    $title = trim($lines[0]);
    $content = implode("\n", array_slice($lines, 4));
    $id = wp_insert_post(array('post_title' => $title, 'post_content' => $content, 'post_status' => 'publish', 'post_author' => 1));
    if ($id) {
        update_post_meta($id, '_wocs_src', $target['name']);
        echo '<p>✅ 등록 완료: ' . esc_html($title) . '</p>';
    }
}
