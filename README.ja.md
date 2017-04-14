# under heavy development

Nata
===
Nata は Google Compute Engine 用のシンプルなWebアプリケーション デプロイツールです．


# Features
- 典型的な Google Compute Engine の構成を1コマンドで展開
- オートスケール
- インスタンスの 無停止 Rolling Update
- Blue-Green Deployment
- Custom Domainに対応

# Usage

## Install

Debian jessie 上で，Python 2.7 と Python 3.4 環境で開発をしています．

```bash
git clone https://github.com/a-r-g-v/nata
sudo python3 setup.py install
```

## Qickstart

Nataを使用するためには，Google Compute Engine上に以下の条件を満たすイメージを作成する必要があります．

- インスタンスを起動するだけで，0.0.0.0:80 に HTTPサービスが提供される
- 正常状態にだけ2xxが返却されるヘルスチェック用のHTTPエンドポイントを持つ (オートスケールの為に必要)

また，イメージファミリとして作成することをお勧めします．

1. Google Cloud Platform側で，Google Compute Engine用のAPIをEnableにします．
1. ServiceAccout用のJSONファイルを入手します．
1. 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` に 上記JSONファイルへのパスを設定します.
1. 環境変数 `NATA_SCHEMA` に SQLAlchemy DSN形式のデータベース接続情報を登録します. （スキーマの初期化は，Nata初回使用時に行われます．）
1. デプロイとプロビジョニング，オートスケール計画を示すためにSpecを作成します，以下を参考にしてください
  (最低限動作させるためには，下記をあなたの環境に合わせたname, project, zone, sourceImages, requestPathに書き換える必要があります．)

```yaml
name: test-app
project: nata-jp
zone: asia-northeast1-a
properties:
  - machineType: g1-small
    canIpForward: True
    disks: 
      - boot: True
        autoDelete: True
        deviceName: test-app
        initializeParams:
          - sourceImage: global/images/family/nata-sampleapp
            diskSizeGb: 10
    networkInterfaces:
      - network: global/networks/default
        accessConfigs:
          - name: external-IP
            type: ONE_TO_ONE_NAT
    scheduling:
      preemptible: True
autoscalingPolicy:
  maxNumReplicas: 10
  minNumRreplicas: 1
  coolDownPeriodSec: 60
  cpuUtilization:
    utilizationTarget: 0.9
enableCDN: False
httpHealthCheck:
  requestPath: /api/v1
  checkIntervalSec: 3
  timeoutSec: 3
LBtimeoutSec: 100
```

1. 上記 Specファイルから`Service`を作成します． `nata service create <path-to-spec-file>`

1. 無事，`Service` の作成が完了したら，`nata service list` で 存在する`Service`の一覧を表示させることができます

# Concepts


## Service

`Service` とは，1つのEndpointと1つ以上の`App`の集合を持つ要素です． 
また，`Service`はただ1つの`Primary App`を持ちます．これは，現在Endpointと関連付いている(公開されている)`App`のことです.

### Endpoint(Lb)
`Endpoint` は 外部公開用 である IPv4アドレスを持ちます．

`Endpoint` は Google Compute Engine 上のリソースである，以下を持ちます．
- global_forwarding_rule_http
- global_forwarding_rule_https
- global_address
- target_http_proxy
- target_https_proxy
- url_map
- backend_service
- http_health_check


## App
`App` は Google Compute Engine上のリソースである，以下を持ちます
- instance_template
- group_manager
- autoscaler
