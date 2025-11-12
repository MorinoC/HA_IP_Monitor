/**
 * HA IP Monitor カスタムLovelaceカード
 * VPS脅威監視用のカスタムダッシュボードカード
 */

class HAIPMonitorCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    // Lovelaceカード設定
    setConfig(config) {
        if (!config.entity) {
            throw new Error('entityを指定してください');
        }
        this.config = config;
        this.render();
    }

    // Home Assistantインスタンスの設定
    set hass(hass) {
        this._hass = hass;
        this.updateCard();
    }

    // カードのレンダリング
    render() {
        this.shadowRoot.innerHTML = `
            <style>
                ${this.getStyles()}
            </style>
            <ha-card header="🛡️ HA IP Monitor">
                <div class="card-content">
                    <div class="status-grid">
                        <div class="status-item" id="blocked-ips">
                            <div class="status-icon">🚫</div>
                            <div class="status-label">被阻止IP</div>
                            <div class="status-value" id="blocked-value">-</div>
                        </div>
                        <div class="status-item" id="ssh-attacks">
                            <div class="status-icon">🔐</div>
                            <div class="status-label">SSH攻击</div>
                            <div class="status-value" id="ssh-value">-</div>
                        </div>
                        <div class="status-item" id="vpn-attacks">
                            <div class="status-icon">🔒</div>
                            <div class="status-label">VPN攻击</div>
                            <div class="status-value" id="vpn-value">-</div>
                        </div>
                        <div class="status-item" id="threat-level">
                            <div class="status-icon">⚠️</div>
                            <div class="status-label">威胁等级</div>
                            <div class="status-value" id="threat-value">-</div>
                        </div>
                    </div>

                    <div class="threat-list">
                        <h3>实时威胁列表</h3>
                        <div id="threat-list-container">
                            <p class="loading">加载中...</p>
                        </div>
                    </div>

                    <div class="actions">
                        <button class="action-button emergency" id="emergency-btn">
                            🚨 紧急锁定
                        </button>
                        <button class="action-button refresh" id="refresh-btn">
                            🔄 刷新数据
                        </button>
                    </div>
                </div>
            </ha-card>
        `;

        this.setupEventListeners();
    }

    // スタイルの定義
    getStyles() {
        return `
            :host {
                display: block;
            }

            ha-card {
                padding: 16px;
            }

            .card-content {
                padding: 0;
            }

            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 12px;
                margin-bottom: 20px;
            }

            .status-item {
                background: var(--primary-background-color);
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                transition: transform 0.2s;
            }

            .status-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }

            .status-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }

            .status-label {
                font-size: 12px;
                color: var(--secondary-text-color);
                margin-bottom: 4px;
            }

            .status-value {
                font-size: 20px;
                font-weight: bold;
                color: var(--primary-text-color);
            }

            .threat-list {
                margin: 20px 0;
            }

            .threat-list h3 {
                font-size: 16px;
                margin: 0 0 12px 0;
                color: var(--primary-text-color);
            }

            #threat-list-container {
                background: var(--primary-background-color);
                border-radius: 8px;
                padding: 12px;
                max-height: 200px;
                overflow-y: auto;
            }

            .threat-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                margin: 4px 0;
                background: var(--card-background-color);
                border-radius: 4px;
                cursor: pointer;
                transition: background 0.2s;
            }

            .threat-item:hover {
                background: var(--secondary-background-color);
            }

            .threat-ip {
                font-family: monospace;
                font-weight: bold;
            }

            .threat-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }

            .threat-badge.high {
                background: #f44336;
                color: white;
            }

            .threat-badge.medium {
                background: #ff9800;
                color: white;
            }

            .threat-badge.low {
                background: #4caf50;
                color: white;
            }

            .actions {
                display: flex;
                gap: 12px;
                margin-top: 16px;
            }

            .action-button {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.2s;
            }

            .action-button.emergency {
                background: #f44336;
                color: white;
            }

            .action-button.emergency:hover {
                background: #d32f2f;
            }

            .action-button.refresh {
                background: var(--primary-color);
                color: white;
            }

            .action-button.refresh:hover {
                opacity: 0.9;
            }

            .loading {
                text-align: center;
                color: var(--secondary-text-color);
                font-style: italic;
            }
        `;
    }

    // イベントリスナーの設定
    setupEventListeners() {
        const emergencyBtn = this.shadowRoot.getElementById('emergency-btn');
        const refreshBtn = this.shadowRoot.getElementById('refresh-btn');

        emergencyBtn?.addEventListener('click', () => this.handleEmergencyLockdown());
        refreshBtn?.addEventListener('click', () => this.handleRefresh());
    }

    // カードの更新
    updateCard() {
        if (!this._hass || !this.config) return;

        // TODO: 実際のエンティティからデータを取得
        const entity = this._hass.states[this.config.entity];

        if (entity) {
            // ステータス値の更新
            this.updateStatusValues(entity);

            // 脅威リストの更新
            this.updateThreatList(entity);
        }
    }

    // ステータス値の更新
    updateStatusValues(entity) {
        const blockedValue = this.shadowRoot.getElementById('blocked-value');
        const sshValue = this.shadowRoot.getElementById('ssh-value');
        const vpnValue = this.shadowRoot.getElementById('vpn-value');
        const threatValue = this.shadowRoot.getElementById('threat-value');

        // TODO: 実際のデータで更新
        if (blockedValue) blockedValue.textContent = '47';
        if (sshValue) sshValue.textContent = '156';
        if (vpnValue) vpnValue.textContent = '38';
        if (threatValue) threatValue.textContent = '中等';
    }

    // 脅威リストの更新
    updateThreatList(entity) {
        const container = this.shadowRoot.getElementById('threat-list-container');

        // TODO: 実際のデータを使用
        const threats = [
            { ip: '185.200.116.43', level: 'high', count: 23 },
            { ip: '207.90.244.11', level: 'medium', count: 12 },
            { ip: '113.11.231.56', level: 'low', count: 5 }
        ];

        container.innerHTML = threats.map(threat => `
            <div class="threat-item">
                <span class="threat-ip">${threat.ip}</span>
                <span class="threat-badge ${threat.level}">
                    ${threat.count} 次攻击
                </span>
            </div>
        `).join('');
    }

    // 緊急ロックダウンの処理
    handleEmergencyLockdown() {
        if (confirm('确定要启动紧急锁定模式吗？')) {
            // TODO: サービスコールを実装
            console.log('Emergency lockdown triggered');
            alert('紧急锁定已启动');
        }
    }

    // リフレッシュの処理
    handleRefresh() {
        // TODO: データの再取得を実装
        console.log('Refresh triggered');
        this.updateCard();
    }

    // カードサイズの取得
    getCardSize() {
        return 5;
    }
}

// カスタム要素の登録
customElements.define('ha-ip-monitor-card', HAIPMonitorCard);

// カード設定の登録
window.customCards = window.customCards || [];
window.customCards.push({
    type: 'ha-ip-monitor-card',
    name: 'HA IP Monitor Card',
    description: 'VPS脅威監視用のカスタムカード',
    preview: false,
    documentationURL: 'https://github.com/cody/HA_IP_Monitor'
});

console.info(
    '%c HA-IP-MONITOR-CARD %c Version 1.0.0 ',
    'color: white; background: #039be5; font-weight: 700;',
    'color: #039be5; background: white; font-weight: 700;'
);
