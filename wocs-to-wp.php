<?php
/**
 * Plugin Name: WOCS Auto Importer
 * Description: wocs.kr GitHub 저장소의 content/ 폴더에서 최신 블로그 글을 가져와 자동 포스팅
 * Version: 1.0
 * Author: WOCS
 */

if (!defined('ABSPATH')) exit;

// ── 설정 ──
define('WOCS_IMPORT_SOURCE', 'https://raw.githubusercontent.com/cryptowoosung/wocs-website-/main/content/');
define('WOCS_IMPORT_INDEX', 'https://api.github.com/repos/cryptowoosung/wocs-website-/contents/content');
define('WOCS_IMPORT_CATEGORY', '글램핑창업');
define('WOCS_IMPORT_META_KEY', '_wocs_source_file');

// ── 플러그인 활성화 시 cron 등록 ──
register_activation_hook(__FILE__, 'wocs_import_activate');
function wocs_import_activate() {
    if (!wp_next_scheduled('wocs_import_cron_hook')) {
        // 다음 오전 9시 (한국시간 KST = UTC+9)
        $next_9am_kst = strtotime('today 00:00:00 UTC'); // UTC 00:00 = KST 09:00
        if ($next_9am_kst < time()) {
            $next_9am_kst = strtotime('tomorrow 00:00:00 UTC');
        }
        wp_schedule_event($next_9am_kst, 'daily', 'wocs_import_cron_hook');
    }
}

// ── 플러그인 비활성화 시 cron 해제 ──
register_deactivation_hook(__FILE__, 'wocs_import_deactivate');
function wocs_import_deactivate() {
    wp_clear_scheduled_hook('wocs_import_cron_hook');
}

// ── cron 실행 함수 등록 ──
add_action('wocs_import_cron_hook', 'wocs_import_run');

// ── 관리자 메뉴에 수동 실행 버튼 추가 ──
add_action('admin_menu', 'wocs_import_admin_menu');
function wocs_import_admin_menu() {
    add_management_page(
        'WOCS Auto Importer',
        'WOCS 임포터',
        'manage_options',
        'wocs-importer',
        'wocs_import_admin_page'
    );
}

function wocs_import_admin_page() {
    echo '<div class="wrap">';
    echo '<h1>WOCS Auto Importer</h1>';

    // 수동 실행
    if (isset($_POST['wocs_run_import']) && check_admin_referer('wocs_run_import_nonce')) {
        echo '<h2>실행 결과:</h2><pre>';
        wocs_import_run(true);
        echo '</pre>';
    }

    // 다음 실행 시간
    $next = wp_next_scheduled('wocs_import_cron_hook');
    if ($next) {
        $kst = $next + (9 * 3600);
        echo '<p><strong>다음 자동 실행:</strong> ' . gmdate('Y-m-d H:i:s', $kst) . ' (KST)</p>';
    } else {
        echo '<p>⚠️ Cron이 등록되어 있지 않습니다. 플러그인을 비활성화 후 재활성화 해주세요.</p>';
    }

    // 최근 임포트 이력
    $imported = get_option('wocs_import_history', array());
    if (!empty($imported)) {
        echo '<h2>최근 임포트 이력:</h2><ul>';
        foreach (array_reverse(array_slice($imported, -10)) as $item) {
            echo '<li>' . esc_html($item) . '</li>';
        }
        echo '</ul>';
    }

    echo '<form method="post">';
    wp_nonce_field('wocs_run_import_nonce');
    echo '<p><input type="submit" name="wocs_run_import" class="button button-primary" value="지금 실행"></p>';
    echo '</form>';
    echo '</div>';
}

// ── 메인 실행 함수 ──
function wocs_import_run($verbose = false) {
    $log = function($msg) use ($verbose) {
        if ($verbose) echo $msg . "\n";
        error_log('[WOCS Importer] ' . strip_tags($msg));
    };

    $log('=== WOCS Auto Importer 시작 ===');

    // GitHub API로 content/ 폴더 파일 목록 가져오기
    $response = wp_remote_get(WOCS_IMPORT_INDEX, array(
        'timeout' => 30,
        'headers' => array('User-Agent' => 'WOCS-Auto-Importer/1.0'),
    ));

    if (is_wp_error($response)) {
        $log('❌ GitHub API 연결 실패: ' . $response->get_error_message());
        return;
    }

    $status_code = wp_remote_retrieve_response_code($response);
    if ($status_code !== 200) {
        $log('❌ GitHub API 응답 오류: HTTP ' . $status_code);
        return;
    }

    $files = json_decode(wp_remote_retrieve_body($response), true);
    if (!is_array($files)) {
        $log('❌ GitHub API 응답 파싱 실패');
        return;
    }

    // auto_post_*.txt 파일만 필터 (최신순 정렬)
    $post_files = array();
    foreach ($files as $file) {
        if (preg_match('/^auto_post_\d{4}-\d{2}-\d{2}_\d+\.txt$/', $file['name'])) {
            $post_files[] = $file['name'];
        }
    }
    rsort($post_files);

    if (empty($post_files)) {
        $log('⚠️ auto_post 파일이 없습니다.');
        return;
    }

    $log('📄 발견된 파일: ' . count($post_files) . '개');

    // 최신 파일부터 최대 3개 처리
    $processed = 0;
    foreach (array_slice($post_files, 0, 3) as $filename) {
        $log("\n📄 처리 중: $filename");

        // 이미 임포트된 파일인지 확인
        $existing = get_posts(array(
            'meta_key'   => WOCS_IMPORT_META_KEY,
            'meta_value' => $filename,
            'post_type'  => 'post',
            'post_status'=> 'any',
            'numberposts'=> 1,
        ));

        if (!empty($existing)) {
            $log("  ⏭️ 이미 포스팅됨 (ID: {$existing[0]->ID}), 건너뜀");
            continue;
        }

        // 파일 내용 가져오기
        $raw_url = WOCS_IMPORT_SOURCE . $filename;
        $file_response = wp_remote_get($raw_url, array(
            'timeout' => 30,
            'headers' => array('User-Agent' => 'WOCS-Auto-Importer/1.0'),
        ));

        if (is_wp_error($file_response)) {
            $log('  ❌ 파일 다운로드 실패: ' . $file_response->get_error_message());
            continue;
        }

        $content = wp_remote_retrieve_body($file_response);
        if (empty($content)) {
            $log('  ⚠️ 파일 내용이 비어있음');
            continue;
        }

        // 파싱: 1행=제목, 2행=날짜, 3행=키워드, 4행=빈줄, 5행~=본문
        $lines = explode("\n", $content);
        if (count($lines) < 5) {
            $log('  ⚠️ 파일 형식 오류 (5행 미만)');
            continue;
        }

        $title = trim($lines[0]);
        $date  = trim($lines[1]);
        $tags  = trim($lines[2]);
        $body  = implode("\n", array_slice($lines, 4));

        // 마크다운 → HTML 간단 변환
        $html_body = wocs_markdown_to_html(trim($body));

        // WOCS 광고 푸터 추가
        $html_body .= "\n\n<hr>\n";
        $html_body .= '<p><strong>글램핑 시공 전문 WOCS</strong> | ';
        $html_body .= '<a href="https://wocs.kr" target="_blank">wocs.kr</a> | ';
        $html_body .= '<a href="tel:01043370582">010-4337-0582</a></p>';

        // 카테고리 ID
        $cat_id = wocs_get_or_create_category();

        // 포스트 생성
        $post_id = wp_insert_post(array(
            'post_title'   => $title,
            'post_content' => $html_body,
            'post_status'  => 'publish',
            'post_date'    => $date . ' 09:00:00',
            'post_category' => $cat_id ? array($cat_id) : array(),
            'tags_input'   => array_map('trim', explode(',', $tags)),
        ));

        if (is_wp_error($post_id)) {
            $log('  ❌ 포스트 생성 실패: ' . $post_id->get_error_message());
            continue;
        }

        // 중복 방지용 meta 저장
        update_post_meta($post_id, WOCS_IMPORT_META_KEY, $filename);

        $log("  ✅ 포스팅 완료! (ID: $post_id) 제목: $title");

        // 이력 저장
        $history = get_option('wocs_import_history', array());
        $history[] = gmdate('Y-m-d H:i:s') . " | ID:$post_id | $filename";
        update_option('wocs_import_history', array_slice($history, -50));

        $processed++;
    }

    $log("\n📊 결과: {$processed}건 포스팅 완료");
    $log('=== WOCS Auto Importer 종료 ===');
}

// ── 카테고리 조회/생성 ──
function wocs_get_or_create_category() {
    $cat = get_term_by('name', WOCS_IMPORT_CATEGORY, 'category');
    if ($cat) return $cat->term_id;

    $result = wp_insert_term(WOCS_IMPORT_CATEGORY, 'category');
    if (!is_wp_error($result)) {
        return $result['term_id'];
    }
    return 0;
}

// ── 마크다운 → HTML 변환 ──
function wocs_markdown_to_html($text) {
    $lines = explode("\n", $text);
    $html = array();
    $in_list = false;

    foreach ($lines as $line) {
        $trimmed = trim($line);

        if ($trimmed === '') {
            if ($in_list) { $html[] = '</ul>'; $in_list = false; }
            continue;
        }

        if (strpos($trimmed, '### ') === 0) {
            $html[] = '<h3>' . substr($trimmed, 4) . '</h3>';
        } elseif (strpos($trimmed, '## ') === 0) {
            $html[] = '<h2>' . substr($trimmed, 3) . '</h2>';
        } elseif (strpos($trimmed, '# ') === 0) {
            $html[] = '<h1>' . substr($trimmed, 2) . '</h1>';
        } elseif (strpos($trimmed, '- ') === 0 || strpos($trimmed, '* ') === 0) {
            if (!$in_list) { $html[] = '<ul>'; $in_list = true; }
            $html[] = '<li>' . substr($trimmed, 2) . '</li>';
        } elseif ($trimmed === '---') {
            $html[] = '<hr>';
        } else {
            $converted = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $trimmed);
            $html[] = '<p>' . $converted . '</p>';
        }
    }

    if ($in_list) $html[] = '</ul>';
    return implode("\n", $html);
}
