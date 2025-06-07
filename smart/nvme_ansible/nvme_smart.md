The SMART/Health Information log page (Log Page Identifier 02h) provides SMART (Self-Monitoring, Analysis, and Reporting Technology) and general health data. This information is retained across power cycles unless otherwise specified. To request this log page for the controller, the namespace identifier must be FFFFFFFFh or 0h. For compatibility with older NVM Express Base Specification revisions (1.4 and earlier), hosts should use a namespace identifier of FFFFFFFFh when requesting the controller log page. [cite_start]The controller may also support per-namespace log page requests, as indicated by the SMART Support bit in the LPA field of the Identify Controller data structure[cite: 21].

If the log page is not supported on a per-namespace basis:
* [cite_start]If the host specifies a namespace identifier other than 0h or FFFFFFFFh, the controller will abort the command with an "Invalid Field in Command" status code[cite: 21].
* [cite_start]If the host specifies a namespace identifier of 0h or FFFFFFFFh, the controller will return the controller log page[cite: 21].

[cite_start]This revision of the specification does not define namespace-specific information in the SMART/Health Information log page; therefore, the controller log page and namespace-specific log page contain identical information[cite: 21].

Critical warnings regarding the NVM subsystem's health can be indicated to the host via an asynchronous event notification. [cite_start]The settings for these warnings, which trigger asynchronous event notifications, are configured using the Set Features command[cite: 21].

Performance can be calculated using parameters from the SMART/Health Information log, such as the number of Read or Write commands, the amount of data read or written, and the controller busy time. These parameters enable the calculation of both I/Os per second and bandwidth. [cite_start]The log page format is defined in Figure 207[cite: 22].

[cite_start]**Figure 207: SMART / Health Information Log Page** [cite: 22]

| Bytes | Description |
|---|---|
| 00 | **Critical Warning (CW)**: This field indicates critical warnings for the controller's state. Each bit corresponds to a critical warning type; multiple bits can be set to '1'. If a bit is cleared to '0', that critical warning does not apply. Critical warnings may trigger an asynchronous event notification to the host. Bits in this field reflect the state at the time the Get Log Page command was processed and may not reflect the state at the time a related asynchronous event notification occurred. |
| | If a bit is set to '1' in one or more Endurance Groups, the corresponding bit in this field must also be set to '1'. |
| | **Bits** | **Description** |
| | 7:4 | Reserved |
| | 3 | **Endurance Group Read-Only (EGRO)**: If set to '1', namespaces in one or more Endurance Groups are in read-only mode for reasons other than a write protection state change. The controller should not set this bit to '1' if the read-only condition is due to a write protection state change of all namespaces in the Endurance Group. |
| | 2 | **NVM Subsystem Degraded Reliability (NDR)**: If set to '1', NVM subsystem reliability has degraded due to significant media errors or internal errors. |
| | 1 | **Endurance Group Available Spare Below (EGASB)**: If set to '1', available spare capacity has fallen below the threshold. |
| | 0 | **Endurance Group Available Spare Capacity Below Threshold (ASCBT)**: If set to '1', the available spare capacity has fallen below the threshold. |
| | **Endurance Group Features (EGFEAT)**: This field defines features of the Endurance Group. |
| 01 | **Bits** | **Description** |
| | 7:1 | Reserved |
| | 0 | **Endurance Group Media (EGRMEDIA)**: If set to '1', the Endurance Group stores data on rotational media. If cleared to '0', it does not store data on rotational media. |
| 02 | Reserved |
| 03 | **Available Spare (AVSP)**: Contains a normalized percentage (0% to 100%) of remaining spare capacity. |
| 04 | **Available Spare Threshold (AVSPT)**: If the available spare falls below this threshold, an asynchronous event completion may occur. The value is a normalized percentage (0% to 100%). Values 101 to 255 are reserved. |
| 05 | **Percentage Used (PUSED)**: A vendor-specific estimate (0% to 100%) of NVM subsystem life used, based on actual usage and manufacturer's prediction. A value of 100 indicates estimated endurance has been consumed, but doesn't necessarily mean NVM subsystem failure. Values exceeding 100 are represented as 255. This value is updated once per power-on hour. Refer to JEDEC JESD218B-02 for SSD device life and endurance measurement techniques. |
| 06-07 | **Domain Identifier (DID)**: This field indicates the identifier of the domain containing this Endurance Group. If the NVM subsystem supports multiple domains, this field should be a non-zero value. If cleared to 0h, the NVM subsystem does not support multiple domains. |
| 08-31 | Reserved |
| 32-47 | **Endurance Estimate (EE)**: An estimate of the total data bytes that can be written to the Endurance Group over its lifetime, assuming a write amplification of 1. Reported in billions (1h = 1,000,000,000 bytes). A value of 0h means the controller does not report an Endurance Estimate. |
| 48-63 | **Data Units Read (DUR)**: Total data bytes read from the Endurance Group (excluding controller reads for internal operations). Reported in thousands (1h = 1,000 units of 512 bytes). A value of 0h means the controller does not report this value. |
| 64-79 | **Data Units Written (DUW)**: Total data bytes written to the Endurance Group (including host and controller writes). Reported in thousands (1h = 1,000 units of 512 bytes). A value of 0h means the controller does not report this value. |
| 80-95 | **Media Units Written (MUW)**: Total data bytes written to the Endurance Group including both host and controller writes (e.g., garbage collection and background media scan operations). Reported in billions (1h = 1,000,000,000 bytes). A value of 0h means the controller does not report this value. |
| 96-111 | **Host Read Commands (HRC)**: Number of SMART Host Read Commands completed by the controller. |
| 112-127 | **Host Write Commands (HWC)**: Number of User Data Out Commands completed by the controller. |
| 128-143 | **Media and Data Integrity Errors (MDIE)**: Number of occurrences where the controller detected an unrecovered data integrity error for the Endurance Group (e.g., uncorrectable ECC, CRC checksum failure, LBA tag mismatch). |
| 144-159 | **Number of Error Information Log Entries (NEILE)**: Number of Error Information Log Entries over the life of the controller for the Endurance Group. |
| 160-175 | **Total Endurance Group Capacity (TEGCAP)**: Total NVM capacity in this Endurance Group in bytes. If cleared to 0h, the NVM subsystem does not report this value. |
| 176-191 | **Unallocated Endurance Group Capacity (UEGCAP)**: Unallocated NVM capacity in this Endurance Group in bytes. If cleared to 0h, the NVM subsystem does not report this value. |
| 192-195 | **Warning Composite Temperature Time (WCTT)**: Time in minutes that the controller was operational and the Composite Temperature was at or above the Warning Composite Temperature Threshold and below the Critical Composite Temperature Threshold. |
| 196-199 | **Critical Composite Temperature Time (CCTT)**: Time in minutes that the controller was operational and the Composite Temperature was at or above the Critical Composite Temperature Threshold. |
| 200-201 | **Temperature Sensor 1 (TSEN1)**: Current temperature reported by temperature sensor 1 in Kelvins. |
| 202-203 | **Temperature Sensor 2 (TSEN2)**: Current temperature reported by temperature sensor 2 in Kelvins. |
| 204-205 | **Temperature Sensor 3 (TSEN3)**: Current temperature reported by temperature sensor 3 in Kelvins. |
| 206-207 | **Temperature Sensor 4 (TSEN4)**: Current temperature reported by temperature sensor 4 in Kelvins. |
| 208-209 | **Temperature Sensor 5 (TSEN5)**: Current temperature reported by temperature sensor 5 in Kelvins. |
| 210-211 | **Temperature Sensor 6 (TSEN6)**: Current temperature reported by temperature sensor 6 in Kelvins. |
| 212-213 | **Temperature Sensor 7 (TSEN7)**: Current temperature reported by temperature sensor 7 in Kelvins. |
| 214-215 | **Temperature Sensor 8 (TSEN8)**: Current temperature reported by temperature sensor 8 in Kelvins. |
| 216-219 | **Thermal Management Temperature 1 Transition Count (TMT1TC)**: Number of times the controller transitioned to lower power active states or performed vendor-specific thermal management actions to minimize performance impact due to the host-controlled thermal management feature. |
| 220-223 | **Thermal Management Temperature 2 Transition Count (TMT2TC)**: Number of times the controller transitioned to lower power active states or performed vendor-specific thermal management actions regardless of performance impact. |
| 224-227 | **Total Time For Thermal Management Temperature 1 (TTTMT1)**: Total time in seconds that the controller was in lower power active states or performing vendor-specific thermal management actions to minimize performance impact due to the host-controlled thermal management feature. |
| 228-231 | **Total Time For Thermal Management Temperature 2 (TTTMT2)**: Total time in seconds that the controller was in lower power active states or performing vendor-specific thermal management actions regardless of performance impact. |
| 232-511 | Reserved |