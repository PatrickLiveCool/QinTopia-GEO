# OPC 证书自动续期与 CDN 部署

服务只处理 `opc.qintopia.cn`，运行于 `122.51.77.220`，不依赖个人电脑、Codex 或网站发布。Python 3 标准库实现。现有主站和 media 的证书服务不变。

## 自动执行

`qintopia-opc-cert.timer` 每小时触发，随机延迟不超过 60 秒，`Persistent=true` 补执行停机期间错过的检查。

1. 查询 OPC 的 CDN 绑定及云端证书，先复用已经签发、可部署、当前有效、覆盖 OPC 且到期时间更晚的新证书。
2. 无可用新证书且剩余有效期不超过 30 天时，通过腾讯云 `ApplyCertificate` 申请 TrustAsia C1 DV Free（类型 83，三个月），使用 `DNS_AUTO`。未过期的旧证书通过 `OldCertificateId` 建立续期关系；已经过期时使用新申请恢复路径。不会调用付费购买接口。
3. 签发等待期间保留当前绑定，每小时重查；已发现的申请不会重复创建。新证书签发后，只写 `Https.CertInfo.CertId`，不更改源站、DNS CNAME、内容服务开关或其他域名。
4. 等待 CDN 配置下发，再使用正常系统信任校验 OPC 域名及实际证书有效期。

当前证书到期时间为北京时间 2027-01-15 12:59:59。若期间没有换证，首次续期窗口从 **2026-12-16 12:59:59** 开始，之后首次定时检查将申请续期。

`DNS_AUTO` 的验证记录由腾讯云 SSL 的现有服务关联角色 `SSL_QCSLinkedRoleInCertificateDependence` 管理。需保持域名在同一腾讯云账号的 DNSPod 托管、该角色可用及免费证书额度可用。CA 拒签、权限或额度不足会记录失败，不会自动购买产品。

## 未发布与已发布的验证

- `HttpsBilling.Switch=off` 时，使用固定 CDN CNAME 连接，并以 `opc.qintopia.cn` 作为 SNI 检查证书。记录模式 `cdn_edge_tls_unpublished`，不会打开 CNAME 或 HTTPS 内容服务，也不把 HTTP 514 认作首页成功。
- HTTPS 内容服务开启后，使用正常公网 DNS 验证 TLS，并确认 OPC 首页最终返回 200 且内容非空；记录模式 `public_tls_and_homepage`。

证书到期时间必须与目标证书相符（允许五分钟误差），旧边缘证书不能算更新成功。证书检查不替代网站上线所需的 COS、CDN 刷新、内容字节及版本 marker 验证。

## 独立身份与权限

CAM 身份和策略编号见 [identity.json](identity.json)，已部署策略见 [policy.json](policy.json)。子账号 `qintopia-opc-cert` 禁止控制台登录。

- 只授予证书查询、免费证书申请、CDN 配置查询和 `opc.qintopia.cn` 的 `ModifyDomainConfig`。
- 申请/查询动作的策略资源为 `*`；代码进一步固定申请域名、免费类型、DNS_AUTO 和有效期。CDN 写操作同时受域名级 CAM 策略与代码中的证书绑定路径校验限制。
- 没有 COS、直接 DNS 写入、付费订单、证书删除或其他 CDN 域名的写权限。没有扩大主站、media 或网站发布账号的权限。
- 凭据只保存在服务器 `/etc/qintopia-opc-cert/credentials.json`，模式 `0600`，由专用无登录系统用户持有；父目录为 root 所有，该用户不能修改父目录。

代码与 systemd 文件由 root 所有。服务以 `qintopia-opc-cert` 用户运行，启用只读系统、禁止提权、home 隔离等保护，仅状态目录可写。定时服务不持有管理员凭据，也不会下载证书私钥。

## 失败恢复

`renewal.json` 在申请前保存申请意图；写操作响应不明确时，先通过证书列表寻找已有订单，禁止盲目重试。若未找到可核对的订单，服务报 `Previous application outcome unknown`。运维人员确认云端确实没有对应申请后，备份状态文件再解除该申请意图；不能直接反复清空状态重新申请。

CDN 绑定更新前保存不含密钥的 `before-*.json`。绑定响应不明或下发未完成时，下一轮重新查询实际绑定后再决策。单轮配置等待最多十分钟；执行超时由 systemd 在十五分钟终止，下一小时继续检查。

签发持续超过 48 小时、订单被拒绝/取消、无已验证替代证书且到期不足七天、实际证书不匹配或首页验证失败，服务返回非零，并写入 `status.json` 与 journal。没有新增对外通知渠道。

## 运维

```sh
sudo systemctl status qintopia-opc-cert.timer
sudo systemctl list-timers qintopia-opc-cert.timer
sudo systemctl start qintopia-opc-cert.service
sudo cat /var/lib/qintopia-opc-cert/status.json
sudo journalctl -u qintopia-opc-cert.service -n 50 --no-pager
```

只读预检（不申请、不绑定新证书）：

```sh
sudo -u qintopia-opc-cert /usr/bin/python3 /opt/qintopia-opc-cert/renew.py
```

暂停自动续期，不改变已经绑定的证书：

```sh
sudo systemctl disable --now qintopia-opc-cert.timer
```

本地测试不访问云端：

```sh
python3 -m unittest discover -s ops/opc-cert-sync -p 'test_*.py' -v
```

## 部署验证

2026-10-17 已按用户授权部署到上述服务器：

- `qintopia-opc-cert.timer` 为 `enabled` / `active`，已设置开机启动；读回的首次计划触发时间为北京时间 2026-10-17 15:00:21。
- 首次 systemd 服务执行时间为北京时间 2026-10-17 14:41:01–14:41:02，`Result=success`、`ExecMainStatus=0`。
- 状态文件记录 `healthy_no_change`、`renewal=not_due`、`certificate_id=bdirFvdi`；验证模式为 `cdn_edge_tls_unpublished`，实际证书有效至北京时间 2027-01-15 12:59:59。
- 已核对本地与服务器 `renew.py` SHA-256 均为 `0bac886f922f7ea4703bb4b2db3c2f79adb295f4d927efb4b9f23f0d5cffb7ed`。
- 专用凭据权限为 `0600`，程序由 root 所有且运行账号不可写；CAM 读回只挂载专用策略 `290174796`，与仓库策略一致。
- 主站证书程序 SHA-256 与本次工作前相同，主站 timer 仍为 active；OPC 的 CNAME 仍禁用，HTTPS 内容服务仍关闭，回源路径仍为 `/opc`。

当前生产证书尚有约 90 天有效期，所以这次没有强制签发新证书或替换绑定。实际首次续期将在上述续期窗口触发；申请、等待签发、绑定及失败恢复路径由隔离测试覆盖，不能把这些测试说成已经发生了一次生产续期。
