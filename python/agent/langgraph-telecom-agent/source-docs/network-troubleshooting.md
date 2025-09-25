# Network Troubleshooting Guide

## Common Network Issues and Solutions

### No Signal / No Service

#### Symptoms
- "No Service" or "Searching" message
- Unable to make calls or send texts
- No data connection

#### Solutions
1. **Toggle Airplane Mode**
   - Turn ON for 30 seconds
   - Turn OFF and wait for reconnection

2. **Restart Device**
   - Power off completely
   - Wait 30 seconds
   - Power on

3. **Check SIM Card**
   - Remove and reinsert SIM
   - Clean SIM contacts with soft cloth
   - Try SIM in another device

4. **Reset Network Settings**
   - iOS: Settings > General > Reset > Reset Network Settings
   - Android: Settings > System > Reset > Reset Network Settings

5. **Update Carrier Settings**
   - iOS: Settings > General > About (prompt appears if update available)
   - Android: Settings > System > Advanced > System Update

### Slow Data Speeds

#### Symptoms
- Web pages loading slowly
- Video buffering frequently
- Apps timing out
- Speed test shows <5 Mbps

#### Solutions
1. **Check Network Type**
   - Ensure 5G/4G is enabled
   - iOS: Settings > Cellular > Cellular Data Options > Voice & Data
   - Android: Settings > Network & Internet > Mobile Network > Preferred Network Type

2. **Clear Cache**
   - Browser cache and cookies
   - App cache for problematic apps
   - System cache partition (Android)

3. **Disable Background Apps**
   - Turn off background app refresh
   - Close unused apps
   - Disable auto-updates on cellular

4. **Check Data Throttling**
   - Verify you haven't exceeded high-speed data limit
   - Check for network congestion in area
   - Consider upgrading plan if consistently throttled

5. **APN Settings Reset**
   - Reset to default ConnectTel APN
   - APN: fast.connecttel.com
   - MMS Proxy: Leave blank
   - Port: 8080

### Call Quality Issues

#### Symptoms
- Dropped calls
- Static or echo
- One-way audio
- Calls not connecting

#### Solutions
1. **Enable HD Voice/VoLTE**
   - Improves call quality significantly
   - iOS: Settings > Cellular > Cellular Data Options > Enable LTE > Voice & Data
   - Android: Settings > Network & Internet > Mobile Network > VoLTE

2. **WiFi Calling Setup**
   - Use when cellular signal is weak
   - Requires stable WiFi (minimum 1 Mbps)
   - Update E911 address for emergency services

3. **Disable Bluetooth**
   - Disconnect Bluetooth devices
   - Test if call quality improves
   - Re-pair devices if needed

4. **Network Selection**
   - Switch from automatic to manual
   - Select ConnectTel network specifically
   - Avoid roaming networks if possible

### Text Message Issues

#### Symptoms
- Messages not sending/receiving
- Delayed message delivery
- Group messages not working
- MMS failures

#### Solutions
1. **Check Message Settings**
   - Verify phone number is correct
   - Enable MMS messaging
   - Check blocked numbers list

2. **Reset Message App**
   - Clear app cache and data
   - Set as default messaging app
   - Update to latest version

3. **iMessage Troubleshooting (iOS)**
   - Sign out and back into iMessage
   - Verify phone number is checked
   - Reset iMessage: Settings > Messages > Send & Receive

4. **RCS Troubleshooting (Android)**
   - Verify RCS is enabled
   - Clear Google Messages cache
   - Re-verify phone number

## Advanced Troubleshooting

### Network Diagnostic Codes

- `*#*#4636#*#*` - Network information (Android)
- `*3001#12345#*` - Field Test Mode (iPhone)
- `*#06#` - Display IMEI
- `*225#` - Account balance check
- `##72786#` - Network reset (carrier-specific)

### Signal Strength Guide

| dBm Range | Signal Quality | Expected Performance |
|-----------|---------------|---------------------|
| -50 to -79 | Excellent | Full speed, no issues |
| -80 to -89 | Good | Normal performance |
| -90 to -99 | Fair | Slower speeds possible |
| -100 to -109 | Poor | Connection issues likely |
| -110+ | No Signal | Service unavailable |

### Tower Connection Issues

1. **Force Tower Refresh**
   - Dial `*228` (CDMA) or `*#*#72786#*#*` (GSM)
   - Select option 2 for roaming update

2. **Preferred Roaming List Update**
   - Ensures connection to newest towers
   - Updates automatically monthly
   - Manual update: `*228` option 2

3. **Band Selection** (Advanced)
   - Some devices allow manual band selection
   - Useful in areas with specific band congestion
   - Access via service menus (device-specific)

## Network Technology Guide

### 5G Networks
- **5G Ultra Wideband**: Fastest speeds (1+ Gbps possible)
- **5G Nationwide**: Broader coverage, moderate speeds
- **Requirements**: 5G-capable device and plan

### 4G LTE
- **LTE+/LTE-A**: Enhanced LTE with carrier aggregation
- **Standard LTE**: Reliable, widespread coverage
- **VoLTE**: Voice over LTE for better call quality

### Network Priorities
1. **Premium Data**: First 50-200GB depending on plan
2. **Standard Data**: After premium allowance
3. **Deprioritized**: During network congestion
4. **Safety Mode**: 128 Kbps after data limit

## When to Contact Support

Contact technical support if:
- Issues persist after all troubleshooting
- Hardware damage suspected
- Account-specific problems
- Multiple devices affected
- Consistent issues in multiple locations

**Support Channels**
- Phone: 1-800-TELECOM (24/7)
- Chat: connecttel.com/support
- App: ConnectTel Mobile App
- Store: Find nearest location