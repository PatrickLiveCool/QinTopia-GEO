# QinTopia CDN 证书自动部署

只维护 `www.qintopia.cn` 的 CDN 证书绑定。该程序运行在 `122.51.77.220` 的 systemd 服务中，不依赖个人电脑或 Codex 保持运行。Python 3 标准库实现，无第三方运行依赖。

## 分工

- Nginx：使用服务器本地证书，为 `qintopia.cn` 提供 HTTPS，并将官网访问跳转到 `www.qintopia.cn`。其既有 webhook 等配置不受本程序影响。
- Certbot：现有开源 ACME 客户端，由 `certbot.timer` 调度，申请/续期/安装 Nginx 的 Let's Encrypt 证书。
- 腾讯云 SSL：管理 CDN 使用的 TrustAsia 证书。2026-10-11 查询到 `AutoRenewFlag=1`，旧证书有续期订单关联，但 `HostingStatus=-1`（未托管部署）。这些元数据不是对以后签发一定成功的保证。
- 本程序：查询腾讯云已颁发的新证书，只更新 `Https.CertInfo.CertId`，随后验证 CDN 状态、实际对外证书及从根域名跳转后的首页。
- COSCLI：上传/同步静态网站文件，不参与本程序的 CDN 证书绑定。

## 自动执行

`qintopia-cdn-cert.timer` 每小时触发，随机延迟不超过 60 秒；`Persistent=true` 会在服务器恢复运行后补执行错过的调度。首次安装也立即执行。已有 Certbot 与 Nginx 保持原样。

新证书必须已颁发、可部署、当前有效、覆盖 `www.qintopia.cn`，并且到期时间严格晚于当前绑定证书。程序拒绝降级、撤销/未生效证书和不匹配的域名；无新证书不重复写入。配置正在下发时最多等待 10 分钟。

更新接口只修改证书 ID，保留源站、DNS、HTTPS 其他设置及所有其他域名。不会启停 CDN、处理余额预警、充值、购买/申请证书或调整账户权限。新的云端证书签发仍由现有腾讯云流程负责。

更新前保存不含证书私钥的绑定元数据。更新响应不明确时退出；下次先重新查询云端状态，不盲目重复写入。验证使用正常 TLS 校验，不忽略证书错误。

## 凭据与权限

使用独立 CAM 子账号 `qintopia-cdn-cert-sync`，禁止控制台登录。只授予 SSL 证书元数据查询、CDN 配置查询，以及资源 `www.qintopia.cn` 的 `ModifyDomainConfig`。IAM 授予的是该域名的配置修改权，代码进一步限制只允许改证书 ID。

服务器密钥文件：`/etc/qintopia-cdn-cert/credentials.json`，权限 `0600`，由专用无登录系统用户 `qintopia-cdn-cert` 持有，父目录不允许该用户写入。密钥不在仓库、日志或聊天中。

systemd 使用独立用户、只读系统目录、禁止访问 home、禁止提权等隔离。可写状态目录为 `/var/lib/qintopia-cdn-cert`。

## 运维与验证

```sh
sudo systemctl status qintopia-cdn-cert.timer
sudo systemctl list-timers qintopia-cdn-cert.timer
sudo systemctl start qintopia-cdn-cert.service
sudo journalctl -u qintopia-cdn-cert.service -n 50 --no-pager
sudo cat /var/lib/qintopia-cdn-cert/status.json
```

成功结果为 `healthy_no_change` 或 `deployed_and_verified`。异常使服务返回非零，记录 systemd 日志和状态文件；不把失败当作部署完成。若无新证书且剩余有效期不足 30 天，也返回失败。本版本没有新增短信、邮件或飞书通知通道。

暂停此自动化（不影响已部署证书、Nginx 或 Certbot）：

```sh
sudo systemctl disable --now qintopia-cdn-cert.timer
```

本地测试（不访问云端、不写生产）：

```sh
python3 -m unittest discover -s ops/cdn-cert-sync -p 'test_*.py' -v
```

## 2026-10-11 恢复记录

- 腾讯云曾明确返回 `CdnUserIsSuspended`，账户欠费 0.30 元。
- 原 500 GB 流量包于 2026-10-08 到期，未用完；新购 500 GB 中国大陆流量包已启用，有效期至 2027-10-11。之后账户欠费清零。
- 人工授权恢复 CDN 服务，并把旧证书 `YpUhggfi` 换绑为 `aNB47uCs`。
- 实际 HTTPS 证书覆盖 `qintopia.cn`、`www.qintopia.cn`，到期北京时间 2026-11-27 06:59:59。
- 根域名跳转后首页返回 200，COS 首页文件正常。
- 原本机 Codex 定时任务已删除，改由本目录的服务器服务执行。
