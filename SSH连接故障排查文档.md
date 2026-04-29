# SSH连接故障排查文档

## 问题描述

尝试连接到远程服务器时出现网络不可达错误:

```bash
ssh root@103.236.97.248 -p 47159
ssh: connect to host 103.236.97.248 port 47159: Network is unreachable
```

**服务器信息:**
- IP地址: 103.236.97.248
- SSH端口: 47159
- 用户名: root
- 连接状态: 首次尝试连接

## 错误分析

`Network is unreachable` 错误表示网络层面无法到达目标服务器,这是一个底层网络连接问题,而不是SSH认证或权限问题。

## 可能的原因

1. **本地网络问题**
   - Mac未连接到互联网
   - 网络配置错误
   - DNS解析问题

2. **服务器配置问题**
   - IP地址或端口号错误
   - 服务器未启动或SSH服务未运行
   - 服务器防火墙阻止连接

3. **网络路由问题**
   - ISP网络问题
   - 防火墙或网络策略阻止
   - 目标网络不可达

4. **VPN或代理问题**
   - 需要通过VPN访问但未连接
   - 代理配置错误

## 排查步骤

### 1. 检查本地网络连接

首先确认Mac已连接到互联网:

```bash
# 测试基本网络连接
ping -c 4 8.8.8.8

# 测试DNS解析
ping -c 4 www.baidu.com
```

**预期结果:** 应该能收到回复,显示网络正常

---

### 2. 测试服务器可达性

检查是否能ping通目标服务器:

```bash
ping -c 4 103.236.97.248
```

**可能的结果:**
- ✅ 收到回复 → 服务器网络可达,继续下一步
- ❌ 请求超时 → 服务器可能关机或防火墙阻止ICMP
- ❌ Network is unreachable → 路由问题,检查网络配置

---

### 3. 测试SSH端口连通性

使用telnet或nc命令测试SSH端口是否开放:

```bash
# 方法1: 使用nc (推荐)
nc -zv 103.236.97.248 47159

# 方法2: 使用telnet
telnet 103.236.97.248 47159
```

**可能的结果:**
- ✅ Connection succeeded → 端口开放,SSH服务运行正常
- ❌ Connection refused → 端口关闭或SSH服务未运行
- ❌ Connection timeout → 防火墙阻止或网络不通

---

### 4. 检查网络路由

追踪到服务器的网络路径:

```bash
traceroute 103.236.97.248
```

这将显示数据包经过的所有路由节点,帮助定位网络中断点。

---

### 5. 检查本地防火墙

确认Mac防火墙没有阻止出站SSH连接:

```bash
# 查看防火墙状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 查看防火墙规则
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps
```

---

### 6. 尝试使用详细模式连接

使用SSH的详细输出模式获取更多信息:

```bash
ssh -vvv root@103.236.97.248 -p 47159
```

这将显示详细的连接过程,帮助定位具体问题。

---

### 7. 检查SSH配置

查看本地SSH配置是否有代理或特殊设置:

```bash
cat ~/.ssh/config
```

---

## 常见解决方案

### 方案1: 确认服务器信息

联系服务器提供方确认:
- IP地址是否正确
- SSH端口是否为47159
- 是否需要通过VPN访问
- 防火墙是否已开放该端口

### 方案2: 检查网络环境

- 确认Mac已连接到正确的网络
- 如果在公司网络,检查是否有出站限制
- 尝试切换到其他网络(如手机热点)测试

### 方案3: 使用VPN

如果服务器在内网或需要特定网络访问:
- 连接到相应的VPN
- 确认VPN路由配置正确

### 方案4: 检查服务器状态

如果有服务器管理权限:
- 确认服务器已启动
- 检查SSH服务状态: `systemctl status sshd`
- 检查防火墙规则: `iptables -L` 或 `firewall-cmd --list-all`
- 确认SSH监听端口: `netstat -tlnp | grep 47159`

### 方案5: 尝试标准SSH端口

如果端口47159不通,尝试标准22端口:

```bash
ssh root@103.236.97.248
```

## 快速诊断命令集

将以下命令依次执行,收集诊断信息:

```bash
# 1. 检查网络连接
ping -c 4 8.8.8.8

# 2. 测试服务器可达性
ping -c 4 103.236.97.248

# 3. 测试端口连通性
nc -zv 103.236.97.248 47159

# 4. 追踪路由
traceroute 103.236.97.248

# 5. 详细SSH连接
ssh -vvv root@103.236.97.248 -p 47159
```

## 下一步行动

根据排查结果:

1. **如果本地网络不通** → 检查网络连接,重启路由器
2. **如果ping不通服务器** → 联系服务器提供方确认状态
3. **如果端口不通** → 确认端口号和防火墙配置
4. **如果需要VPN** → 连接VPN后重试
5. **如果所有测试都失败** → 联系网络管理员或服务器提供方

## 联系信息

在联系技术支持时,请提供:
- 错误信息截图
- 上述诊断命令的输出结果
- 你的网络环境(家庭/公司/公共网络)
- 是否使用VPN或代理

---

## 诊断结果

### 测试执行情况

✅ **本地网络连接正常**
```
ping 8.8.8.8 - 成功 (延迟92-268ms)
ping www.baidu.com - 成功 (延迟43-63ms)
```

✅ **服务器网络可达**
```
ping 103.236.97.248 - 成功 (延迟57-117ms)
```

❌ **SSH端口不可达**
```
nc -zv 103.236.97.248 47159 - 失败 (Network is unreachable)
ssh -p 47159 - 失败 (Network is unreachable)
```

❌ **路由追踪异常**
```
traceroute在第2跳后中断,无法到达目标
```

### 问题分析

**核心问题:** ICMP ping能通,但TCP端口47159连接失败

这种情况通常表明:

1. **服务器端SSH服务配置问题**
   - SSH服务可能没有监听在端口47159
   - SSH服务可能只监听在标准端口22
   - SSH服务可能未启动

2. **服务器防火墙配置**
   - 防火墙允许ICMP(ping)通过
   - 但阻止了TCP端口47159的入站连接
   - 这是最可能的原因

3. **SSH配置文件问题**
   - 发现 `~/.ssh/config` 中有9个重复的 `103.236.97.248` 配置
   - 虽然不太可能导致"Network is unreachable",但应该清理

### 建议解决方案

#### 方案1: 尝试标准SSH端口 (推荐首先尝试)

```bash
# 尝试连接标准22端口
ssh root@103.236.97.248

# 或者明确指定22端口
ssh root@103.236.97.248 -p 22
```

如果22端口能连接成功,说明:
- 服务器SSH服务正常运行
- 但没有在47159端口监听
- 需要联系服务器管理员确认正确的端口号

#### 方案2: 清理SSH配置文件

你的 `~/.ssh/config` 中有9个重复的配置块,建议清理:

```bash
# 备份当前配置
cp ~/.ssh/config ~/.ssh/config.backup

# 编辑配置文件
nano ~/.ssh/config
```

删除重复的配置,只保留一个:
```
Host 103.236.97.248
  HostName 103.236.97.248
  User root
  Port 47159
```

#### 方案3: 联系服务器管理员

需要确认以下信息:
1. SSH服务是否在端口47159上监听?
2. 服务器防火墙是否开放了47159端口?
3. 是否需要先通过VPN或跳板机访问?
4. 正确的SSH端口号是多少?

服务器管理员需要检查:
```bash
# 检查SSH监听端口
netstat -tlnp | grep sshd
# 或
ss -tlnp | grep sshd

# 检查防火墙规则
iptables -L -n | grep 47159
# 或
firewall-cmd --list-ports

# 检查SSH配置
grep Port /etc/ssh/sshd_config
```

#### 方案4: 使用代理或跳板机

如果服务器在内网或有特殊网络限制,可能需要:
- 连接VPN后再尝试
- 通过跳板机(堡垒机)连接
- 使用SSH隧道或端口转发

### 下一步行动

1. **立即尝试:** `ssh root@103.236.97.248` (不指定端口,使用默认22)
2. **如果22端口能通:** 说明端口号信息有误,使用22端口即可
3. **如果22端口也不通:** 联系服务器提供方确认:
   - 服务器是否正常运行
   - SSH服务是否启动
   - 正确的访问方式
4. **清理SSH配置:** 删除重复的配置块

---

**文档创建时间:** 2026年4月23日  
**诊断时间:** 2026年4月23日 19:52  
**问题状态:** ✅ 已解决 - 使用标准22端口可连接,但需要正确密码

---

## 最终解决方案

### 问题已定位

✅ **SSH连接成功!**

使用标准22端口可以成功连接到服务器:
```bash
ssh root@103.236.97.248
```

**结论:**
- 服务器SSH服务运行在标准端口22,而不是47159
- 端口47159可能未开放或SSH服务未在该端口监听
- 原始连接命令中的端口号信息有误

### 当前状态

现在遇到的是密码认证问题,这是正常的SSH认证流程:
```
root@103.236.97.248's password: 
Permission denied, please try again.
```

这说明:
1. ✅ 网络连接正常
2. ✅ SSH服务正常运行
3. ❌ 输入的密码不正确

### 解决密码问题

#### 选项1: 使用正确的密码

联系服务器管理员或查看服务器提供方给你的凭证信息,获取正确的root密码。

#### 选项2: 使用SSH密钥认证(推荐)

密钥认证比密码更安全,设置步骤:

1. **生成SSH密钥对**(如果还没有):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. **将公钥复制到服务器**:
```bash
ssh-copy-id root@103.236.97.248
```
这会要求输入一次密码,之后就可以免密登录。

3. **或者手动添加公钥**:
```bash
# 查看你的公钥
cat ~/.ssh/id_ed25519.pub

# 然后联系服务器管理员,将公钥内容添加到服务器的
# /root/.ssh/authorized_keys 文件中
```

#### 选项3: 检查是否有其他用户名

有时候root账户可能被禁用,尝试使用其他用户名:
```bash
ssh admin@103.236.97.248
ssh ubuntu@103.236.97.248
ssh centos@103.236.97.248
```

### 更新SSH配置

既然确认端口是22而不是47159,建议更新 `~/.ssh/config`:

```bash
# 备份配置
cp ~/.ssh/config ~/.ssh/config.backup

# 编辑配置
nano ~/.ssh/config
```

将所有 `103.236.97.248` 的配置改为:
```
Host myserver
  HostName 103.236.97.248
  User root
  Port 22
  # 如果使用密钥认证,添加:
  # IdentityFile ~/.ssh/id_ed25519
```

之后就可以简单地使用:
```bash
ssh myserver
```

### 总结

**原始问题:** 端口47159不可达  
**根本原因:** SSH服务运行在标准22端口,而不是47159  
**解决方法:** 使用 `ssh root@103.236.97.248` (默认22端口)  
**下一步:** 获取正确的密码或配置SSH密钥认证

---

## 密码认证失败问题

### 问题描述

虽然SSH连接成功,但密码认证失败:
```
root@103.236.97.248's password: 
Permission denied, please try again.
```

用户确认密码是正确的,但仍然无法登录。

### 可能的原因

1. **密码输入问题**
   - 密码包含特殊字符,在终端输入时可能被误解
   - 复制粘贴时包含了额外的空格或换行符
   - 键盘布局问题(大小写锁定、输入法等)

2. **服务器配置限制**
   - SSH配置禁用了root用户的密码登录
   - 服务器要求使用密钥认证
   - PAM配置限制了登录

3. **账户状态问题**
   - root账户被锁定
   - 密码已过期需要重置
   - 账户权限配置问题

### 排查步骤

#### 1. 检查SSH服务器配置

服务器的 `/etc/ssh/sshd_config` 可能禁用了root密码登录:
```bash
# 服务器管理员需要检查:
grep "PermitRootLogin" /etc/ssh/sshd_config
grep "PasswordAuthentication" /etc/ssh/sshd_config
```

常见的限制配置:
- `PermitRootLogin no` - 完全禁止root登录
- `PermitRootLogin without-password` - 只允许密钥登录,不允许密码
- `PermitRootLogin prohibit-password` - 同上(新版本)
- `PasswordAuthentication no` - 禁用密码认证

#### 2. 尝试使用其他用户

如果root被限制,尝试使用普通用户登录:
```bash
# 常见的默认用户名
ssh admin@103.236.97.248
ssh ubuntu@103.236.97.248
ssh centos@103.236.97.248
ssh user@103.236.97.248
```

登录后再切换到root:
```bash
sudo su -
# 或
sudo -i
```

#### 3. 使用SSH密钥认证

如果服务器要求密钥认证,需要配置SSH密钥:

**步骤1: 生成密钥对**
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 或使用RSA
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

**步骤2: 获取公钥**
```bash
cat ~/.ssh/id_ed25519.pub
# 或
cat ~/.ssh/id_rsa.pub
```

**步骤3: 将公钥添加到服务器**

联系服务器管理员,将公钥内容添加到服务器的:
```
/root/.ssh/authorized_keys
```

或者如果你有其他方式访问服务器(如控制面板),可以直接添加。

**步骤4: 使用密钥登录**
```bash
ssh -i ~/.ssh/id_ed25519 root@103.236.97.248
```

#### 4. 检查密码输入

**方法1: 使用sshpass工具**
```bash
# 安装sshpass (Mac)
brew install sshpass

# 使用sshpass避免手动输入
sshpass -p 'your_password' ssh root@103.236.97.248
```

**方法2: 将密码写入文件测试**
```bash
# 创建临时密码文件
echo 'your_password' > /tmp/pass.txt
chmod 600 /tmp/pass.txt

# 使用sshpass从文件读取
sshpass -f /tmp/pass.txt ssh root@103.236.97.248

# 测试完删除
rm /tmp/pass.txt
```

#### 5. 查看详细的认证日志

使用更详细的调试模式:
```bash
ssh -vvv root@103.236.97.248 2>&1 | grep -i "auth\|password\|permission"
```

这会显示认证过程的详细信息。

### 解决方案

#### 方案1: 联系服务器管理员

请管理员确认:
1. root账户是否允许密码登录?
2. 是否必须使用SSH密钥?
3. 是否有其他用户可以登录?
4. 密码是否正确且未过期?

#### 方案2: 使用服务器控制面板

如果服务器有Web控制面板(如阿里云、腾讯云等):
1. 登录控制面板
2. 使用VNC或Web终端直接访问
3. 重置root密码或添加SSH密钥
4. 检查SSH配置

#### 方案3: 配置SSH密钥(推荐)

这是最安全和便捷的方式:
1. 生成SSH密钥对
2. 通过控制面板或管理员添加公钥到服务器
3. 使用密钥登录,无需密码

#### 方案4: 修改服务器SSH配置

如果你有其他方式访问服务器,可以修改SSH配置:

```bash
# 编辑SSH配置
sudo nano /etc/ssh/sshd_config

# 确保以下配置:
PermitRootLogin yes
PasswordAuthentication yes

# 重启SSH服务
sudo systemctl restart sshd
# 或
sudo service sshd restart
```

### 快速诊断命令

```bash
# 1. 尝试其他用户
ssh admin@103.236.97.248

# 2. 使用详细模式查看认证过程
ssh -vvv root@103.236.97.248

# 3. 如果有密钥,尝试密钥登录
ssh -i ~/.ssh/id_rsa root@103.236.97.248

# 4. 检查本地是否有保存的密钥
ls -la ~/.ssh/
```

### 总结

**当前状态:** SSH连接成功,但密码认证失败  
**最可能原因:** 服务器配置禁用了root密码登录,要求使用密钥认证  
**推荐方案:** 配置SSH密钥认证或使用其他用户登录后切换到root  
**下一步:** 联系服务器管理员确认认证方式,或配置SSH密钥
