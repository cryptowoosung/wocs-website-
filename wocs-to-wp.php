<?php
/*
Plugin Name: WOCS Auto Importer
Plugin URI: https://wocs.kr
Description: GitHub의 wocs-website content/ 폴더에서 블로그 글을 가져와 자동 포스팅합니다.
Version: 1.1
Author: WOCS
Author URI: https://wocs.kr
License: GPL2
*/

// 직접 접근 차단
defined('ABSPATH') || die('Direct access not allowed.');

/**
 * WOCS Auto Importer 플러그인 클래스
 */
class WOCS_Auto_Importer {

    const VERSION        = '1.1';
    const SOURCE_BASE    = 'https://raw.githubusercontent.com/cryptowoosung/wocs-website-/main/content/';
    const INDEX_API      = 'https://api.github.com/repos/cryptowoosung/wocs-website-/contents/content';
    const CATEGORY_NAME  = '글램핑창업';
    const META_KEY       = '_wocs_source_file';
    const CRON_HOOK      = 'wocs_auto_import_daily';
    const MENU_SLUG      = 'wocs-auto-importer';
    const OPTION_HISTORY = 'wocs_import_history';

    /**
     * 싱글톤 인스턴스
     */
    private static $instance = null;

    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * 생성자: 훅 등록
     */
    private function __construct() {
        // 관리자 메뉴
        add_action('admin_menu', array($this, 'register_admin_menu'));

        // Cron 실행
        add_action(self::CRON_HOOK, array($this, 'run_import'));

        // 플러그인 활성화/비활성화
        register_activation_hook(__FILE__, array($this, 'on_activate'));
        register_deactivation_hook(__FILE__, array($this, 'on_deactivate'));

        // 플러그인 목록에 "설정" 링크 추가
        add_filter('plugin_action_links_' . plugin_basename(__FILE__), array($this, 'add_settings_link'));
    }

    /**
     * 활성화: cron 등록
     */
    public function on_activate() {
        if (!wp_next_scheduled(self::CRON_HOOK)) {
            // UTC 00:00 = KST 09:00
            $next_run = strtotime('today 00:00:00 UTC');
            if ($next_run < time()) {
                $next_run = strtotime('tomorrow 00:00:00 UTC');
            }
            wp_schedule_event($next_run, 'daily', self::CRON_HOOK);
        }
    }

    /**
     * 비활성화: cron 해제
     */
    public function on_deactivate() {
        wp_clear_scheduled_hook(self::CRON_HOOK);
    }

    /**
     * 플러그인 목록에 "설정" 링크
     */
    public function add_settings_link($links) {
        $url = admin_url('tools.php?page=' . self::MENU_SLUG);
        $links[] = '<a href="' . esc_url($url) . '">설정</a>';
        return $links;
    }

    /**
     * 관리자 메뉴 등록
     */
    public function register_admin_menu() {
        add_submenu_page(
            'tools.php',                    // 부모 메뉴: 도구
            'WOCS Auto Importer',           // 페이지 타이틀
            'WOCS 임포터',                   // 메뉴 타이틀
            'manage_options',               // 권한
            self::MENU_SLUG,                // 슬러그
            array($this, 'render_admin_page') // 콜백
        );
    }

    /**
     * 관리 페이지 렌더링
     */
    public function render_admin_page() {
        // 권한 확인
        if (!current_user_can('manage_options')) {
            wp_die('권한이 없습니다.');
        }

        echo '<div class="wrap">';
        echo '<h1>WOCS Auto Importer <small>v' . self::VERSION . '</small></h1>';
        echo '<hr>';

        // 수동 실행 처리
        if (isset($_POST['wocs_run_now'])) {
            if (!wp_verify_nonce($_POST['_wpnonce'], 'wocs_import_nonce')) {
                wp_die('보안 검증 실패');
            }
            echo '<div class="notice notice-info"><p><strong>실행 결과:</strong></p></div>';
            echo '<pre style="background:#f1f1f1;padding:15px;border:1px solid #ccc;max-height:500px;overflow:auto;">';
            $this->run_import(true);
            echo '</pre>';
            echo '<hr>';
        }

        // 상태 정보
        echo '<h2>상태</h2>';
        echo '<table class="widefat fixed" style="max-width:600px;">';

        // 플러그인 상태
        echo '<tr><td><strong>플러그인 파일</strong></td><td>' . esc_html(plugin_basename(__FILE__)) . '</td></tr>';

        // Cron 상태
        $next = wp_next_scheduled(self::CRON_HOOK);
        if ($next) {
            $kst_time = gmdate('Y-m-d H:i:s', $next + (9 * 3600));
            echo '<tr><td><strong>다음 자동 실행</strong></td><td>' . $kst_time . ' (KST)</td></tr>';
        } else {
            echo '<tr><td><strong>다음 자동 실행</strong></td>';
            echo '<td style="color:red;">Cron 미등록 — 플러그인을 비활성화 후 재활성화 하세요</td></tr>';
        }

        // 소스 URL
        echo '<tr><td><strong>데이터 소스</strong></td><td><a href="' . esc_url(self::INDEX_API) . '" target="_blank">GitHub API</a></td></tr>';
        echo '<tr><td><strong>카테고리</strong></td><td>' . esc_html(self::CATEGORY_NAME) . '</td></tr>';

        echo '</table>';

        // 최근 이력
        $history = get_option(self::OPTION_HISTORY, array());
        if (!empty($history)) {
            echo '<h2>최근 임포트 이력</h2>';
            echo '<table class="widefat fixed" style="max-width:600px;">';
            echo '<thead><tr><th>시간 (UTC)</th><th>포스트 ID</th><th>파일명</th></tr></thead><tbody>';
            foreach (array_reverse(array_slice($history, -10)) as $item) {
                $parts = array_map('trim', explode('|', $item));
                echo '<tr>';
                foreach ($parts as $p) {
                    echo '<td>' . esc_html($p) . '</td>';
                }
                echo '</tr>';
            }
            echo '</tbody></table>';
        } else {
            echo '<p>아직 임포트 이력이 없습니다.</p>';
        }

        // 수동 실행 버튼
        echo '<h2>수동 실행</h2>';
        echo '<form method="post">';
        wp_nonce_field('wocs_import_nonce');
        echo '<p>GitHub에서 최신 글을 가져와 포스팅합니다.</p>';
        submit_button('지금 실행', 'primary', 'wocs_run_now');
        echo '</form>';

        echo '</div>';
    }

    /**
     * 메인 임포트 실행
     */
    public function run_import($verbose = false) {
        $log = function($msg) use ($verbose) {
            if ($verbose) echo esc_html($msg) . "\n";
            error_log('[WOCS Importer] ' . strip_tags($msg));
        };

        $log('=== WOCS Auto Importer 시작 (' . gmdate('Y-m-d H:i:s') . ' UTC) ===');

        // 1. GitHub API로 파일 목록 가져오기
        $response = wp_remote_get(self::INDEX_API, array(
            'timeout' => 30,
            'headers' => array('User-Agent' => 'WOCS-Auto-Importer/' . self::VERSION),
        ));

        if (is_wp_error($response)) {
            $log('GitHub API 연결 실패: ' . $response->get_error_message());
            return;
        }

        $code = wp_remote_retrieve_response_code($response);
        if ($code !== 200) {
            $log('GitHub API 오류: HTTP ' . $code);
            $log('응답: ' . wp_remote_retrieve_body($response));
            return;
        }

        $files = json_decode(wp_remote_retrieve_body($response), true);
        if (!is_array($files)) {
            $log('GitHub API 응답 파싱 실패');
            return;
        }

        // 2. auto_post_*.txt 파일 필터
        $post_files = array();
        foreach ($files as $file) {
            if (isset($file['name']) && preg_match('/^auto_post_\d{4}-\d{2}-\d{2}_\d+\.txt$/', $file['name'])) {
                $post_files[] = $file['name'];
            }
        }
        rsort($post_files);

        if (empty($post_files)) {
            $log('auto_post 파일 없음');
            return;
        }

        $log('발견된 파일: ' . count($post_files) . '개');

        // 3. 최신 3개 처리
        $processed = 0;
        foreach (array_slice($post_files, 0, 3) as $filename) {
            $log('');
            $log('처리 중: ' . $filename);

            // 중복 확인
            $existing = get_posts(array(
                'meta_key'    => self::META_KEY,
                'meta_value'  => $filename,
                'post_type'   => 'post',
                'post_status' => 'any',
                'numberposts' => 1,
            ));

            if (!empty($existing)) {
                $log('  이미 포스팅됨 (ID: ' . $existing[0]->ID . '), 건너뜀');
                continue;
            }

            // 파일 다운로드
            $raw_url = self::SOURCE_BASE . rawurlencode($filename);
            $file_res = wp_remote_get($raw_url, array(
                'timeout' => 30,
                'headers' => array('User-Agent' => 'WOCS-Auto-Importer/' . self::VERSION),
            ));

            if (is_wp_error($file_res)) {
                $log('  파일 다운로드 실패: ' . $file_res->get_error_message());
                continue;
            }

            $content = wp_remote_retrieve_body($file_res);
            if (empty(trim($content))) {
                $log('  파일 내용 비어있음');
                continue;
            }

            // 파싱: 1행=제목, 2행=날짜, 3행=키워드, 4행=빈줄, 5행~=본문
            $lines = explode("\n", $content);
            if (count($lines) < 5) {
                $log('  파일 형식 오류 (5행 미만)');
                continue;
            }

            $title = sanitize_text_field(trim($lines[0]));
            $date  = sanitize_text_field(trim($lines[1]));
            $tags  = sanitize_text_field(trim($lines[2]));
            $body  = implode("\n", array_slice($lines, 4));

            $log('  제목: ' . $title);

            // 마크다운 → HTML
            $html_body = $this->markdown_to_html(trim($body));

            // WOCS 푸터
            $html_body .= "\n\n<hr>\n";
            $html_body .= '<p><strong>글램핑 시공 전문 WOCS</strong> | ';
            $html_body .= '<a href="https://wocs.kr" target="_blank" rel="noopener">wocs.kr</a> | ';
            $html_body .= '<a href="tel:01043370582">010-4337-0582</a></p>';

            // 카테고리
            $cat_id = $this->get_or_create_category();

            // 날짜 검증
            if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
                $date = current_time('Y-m-d');
            }

            // 포스트 생성
            $post_id = wp_insert_post(array(
                'post_title'    => $title,
                'post_content'  => $html_body,
                'post_status'   => 'publish',
                'post_date'     => $date . ' 09:00:00',
                'post_category' => $cat_id ? array($cat_id) : array(),
                'tags_input'    => array_map('trim', explode(',', $tags)),
            ), true);

            if (is_wp_error($post_id)) {
                $log('  포스트 생성 실패: ' . $post_id->get_error_message());
                continue;
            }

            // 메타 저장 (중복 방지)
            update_post_meta($post_id, self::META_KEY, $filename);

            $log('  포스팅 완료! ID: ' . $post_id);
            $log('  URL: ' . get_permalink($post_id));

            // 이력 저장
            $history = get_option(self::OPTION_HISTORY, array());
            $history[] = gmdate('Y-m-d H:i:s') . ' | ID:' . $post_id . ' | ' . $filename;
            update_option(self::OPTION_HISTORY, array_slice($history, -50));

            $processed++;
        }

        $log('');
        $log('결과: ' . $processed . '건 포스팅 완료');
        $log('=== WOCS Auto Importer 종료 ===');
    }

    /**
     * 카테고리 조회/생성
     */
    private function get_or_create_category() {
        $cat = get_term_by('name', self::CATEGORY_NAME, 'category');
        if ($cat) return $cat->term_id;

        $result = wp_insert_term(self::CATEGORY_NAME, 'category');
        if (!is_wp_error($result)) {
            return $result['term_id'];
        }
        return 0;
    }

    /**
     * 마크다운 → HTML
     */
    private function markdown_to_html($text) {
        $lines = explode("\n", $text);
        $html = array();
        $in_list = false;

        foreach ($lines as $line) {
            $t = trim($line);

            if ($t === '') {
                if ($in_list) { $html[] = '</ul>'; $in_list = false; }
                continue;
            }

            if (strpos($t, '### ') === 0) {
                $html[] = '<h3>' . esc_html(substr($t, 4)) . '</h3>';
            } elseif (strpos($t, '## ') === 0) {
                $html[] = '<h2>' . esc_html(substr($t, 3)) . '</h2>';
            } elseif (strpos($t, '# ') === 0) {
                $html[] = '<h1>' . esc_html(substr($t, 2)) . '</h1>';
            } elseif (strpos($t, '- ') === 0 || strpos($t, '* ') === 0) {
                if (!$in_list) { $html[] = '<ul>'; $in_list = true; }
                $html[] = '<li>' . esc_html(substr($t, 2)) . '</li>';
            } elseif ($t === '---') {
                $html[] = '<hr>';
            } else {
                $escaped = esc_html($t);
                $converted = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $escaped);
                $html[] = '<p>' . $converted . '</p>';
            }
        }

        if ($in_list) $html[] = '</ul>';
        return implode("\n", $html);
    }
}

// 플러그인 초기화
WOCS_Auto_Importer::get_instance();
