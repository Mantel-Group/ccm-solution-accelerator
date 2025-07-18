# Continuous Controls Monitoring - Metric Library

## List of metrics

| Metric ID                | Description      | Executive | Management |
|--------------------------|------------------|-----------|------------|
| **IM01** | Identity - % of users active | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **IM02** | Identity - % of users without expired passwords | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM01** | Vulnerability - % of systems without Operating System Vulnerabilities | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM02** | Vulnerability - % of systems without Application Vulnerabilities | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM03** | Vulnerability - % of systems without Critical Vulnerabilities published over 48 hours ago | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM04** | Vulnerability - % of systems without Critical Vulnerabilities published over 2 weeks ago | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM05** | Vulnerability - % of systems without Critical Vulnerabilities published over 1 month ago | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **VM06** | Vulnerability - % of systems without unpatchable explotable vulnerabilities | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **US01** | User Security - % of users who have completed Security Awareness training in the last 12 months | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **US02** | User Security - % of users who have completed Security Awareness training | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **OP01** | Operations - % of hosts detected in the last 30 days | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **NS01** | Network Security - % of domains with insecure ports | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |
| **NS02** | Network Security - % of domains with valid TLS certificates | ![yes](https://img.shields.io/badge/YES-0000F0) | ![yes](https://img.shields.io/badge/YES-0000F0) |


## Metric Details
### IM01 - Identity - % of users active

#### Description

Dormant identity accounts pose a significant threat to information security as they create a potential loophole allowing unauthorised access or exploitation since these inactive accounts may go unnoticed and lack the regular monitoring and security measures applied to active user profiles.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `IM01`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | user                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||IM - Identity Management|IM - Identity Management - Hygiene|
|MCSB||Privileged Access|Manage lifecycle of identities and entitlements|
|PCI DSS v4.0||Requirement 8: Identify Users and Authenticate Access to System Components|8.2.6 Inactive user accounts are removed or disabled within 90 days of inactivity.|
|ISO27001:2022||8 Technological controls|Secure authentication technologies and procedures shall be implemented based on information access restrictions and the topic-specific policy on access control.|
|NIST CSF v1.1||PROTECT (PR)|Users, devices, and other assets are authenticated (e.g., single-factor, multi-factor) commensurate with the risk of the transaction (e.g., individuals' security and privacy risks and other organizational risks)|
|NIST CSF v2.0||PROTECT (PR)|PR.AA-03: Users, services, and hardware are authenticated|
|CIS 8.1||Account Management||



### IM02 - Identity - % of users without expired passwords

#### Description

Rotating of passwords is a good security practice. Ensure passwords are rotated frequently.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `IM02`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | user                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|ISO27001:2013||9 Access control|Password management system|
|PCI DSS v4.0||Requirement 8: Identify Users and Authenticate Access to System Components|8.3.9 If passwords/passphrases are used as the only authentication factor for user access (i.e., in any single-factor authentication implementation) then either: • Passwords/passphrases are changed at least once every 90 days,  OR • The security posture of accounts is dynamically analyzed, and real-time access to resources is automatically determined accordingly.  Applicability Notes This requirement applies to in-scope system components that are not in the CDE because these components are not subject to MFA requirements. This requirement is not intended to apply to user accounts on point-of-sale terminals that have access to only one card number at a time to facilitate a single transaction (such as IDs used by cashiers on point-of-sale terminals). This requirement does not apply to service providers' customer accounts but does apply to accounts for service provider personnel.|
|NIST CSF v1.1||PROTECT (PR)|Identities are proofed and bound to credentials and asserted in interactions|
|ISO27001:2022||8 Technological controls|Secure authentication technologies and procedures shall be implemented based on information access restrictions and the topic-specific policy on access control.|
|NIST CSF v2.0||PROTECT (PR)|PR.AA-02: Identities are proofed and bound to credentials based on the context of interactions|
|CIS 8.1||Account Management||



### VM01 - Vulnerability - % of systems without Operating System Vulnerabilities

#### Description

Operating System vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM01`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.8                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|



### VM02 - Vulnerability - % of systems without Application Vulnerabilities

#### Description

Application vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM02`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|



### VM03 - Vulnerability - % of systems without Critical Vulnerabilities published over 48 hours ago

#### Description

Vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM03`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.8                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in drivers are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in firmware are applied within 48 hours of release when vulnerabilities are assessed as critical by vendors or when working exploits exist.|



### VM04 - Vulnerability - % of systems without Critical Vulnerabilities published over 2 weeks ago

#### Description

Vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM04`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.8                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within two weeks of release.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within two weeks of release.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within two weeks of release.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within two weeks of release.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML1||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in online services are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of internet-facing servers and internet-facing network devices are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within two weeks of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|



### VM05 - Vulnerability - % of systems without Critical Vulnerabilities published over 1 month ago

#### Description

Vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM05`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.8                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within one month of release.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within one month of release.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in applications other than office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within one month of release.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in applications other than office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within one month of release.|
|Essential8-ML1||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within one month of release.|
|Essential8-ML2||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within one month of release.|
|Essential8-ML2||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in applications other than office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within one month of release.|
|Essential8-ML3||Patch applications|Patches, updates or other vendor mitigations for vulnerabilities in applications other than office productivity suites, web browsers and their extensions, email clients, PDF software, and security products are applied within one month of release.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in drivers are applied within one month of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in operating systems of workstations, non-internet-facing servers and non-internet-facing network devices are applied within one month of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|
|Essential8-ML3||Patch operating systems|Patches, updates or other vendor mitigations for vulnerabilities in firmware are applied within one month of release when vulnerabilities are assessed as non-critical by vendors and no working exploits exist.|



### VM06 - Vulnerability - % of systems without unpatchable explotable vulnerabilities

#### Description

Vulnerabilities post a significant risk, and need to be remediated as soon as possible.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `VM06`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.8                                                                    |
| **Resource Type** | system                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||VM - Vulnerability Management|VM - Vulnerability Management - Risk|
|CPS 230||Operational risk management|An APRA-regulated entity must maintain appropriate and sound information and information technology (IT) infrastructure to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, an APRA-regulated entity must monitor the age and health of its IT infrastructure and meet the requirements for information security in Prudential Standard CPS 234 Information Security (CPS 234)|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must assess the impact of its business and strategic decisions on its operational risk profile and operational resilience, as part of its business and strategic planning processes. This must include an assessment of the impact of new products, services, geographies and technologies on its operational risk profile.|
|CPS 230||Operational risk controls|An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.|
|CPS 230||Business Continuity - Critical operations and tolerance levels|Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.|
|CPS 230||Operational risk profile and assessment|An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, an APRA-regulated entity must: a) maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management;|
|CPS 230||Management of service provider arrangements|An APRA-regulated entity must maintain a comprehensive service provider management policy that sets out how it will identify material service providers and manage the arrangements with such providers, including the management of material risks associated with the arrangements.|
|CIS 8.1||Continuous Vulnerability Management||
|NIST CSF v2.0||IDENTIFY (ID)|ID.RA-01: Vulnerabilities in assets are identified, validated, and recorded|
|ISO27001:2013||12 Operations security|Management of technical vulnerabilities|
|ISO27001:2022||8 Technological controls|Information about technical vulnerabilities of information systems in use shall be obtained, the organization's exposure to such vulnerabilities shall be evaluated and appropriate measures shall be taken.|



### US01 - User Security - % of users who have completed Security Awareness training in the last 12 months

#### Description

Regular security awareness training will reduce the risk of human error by providing awareness of security issues to your team.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `US01`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | user                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||US - User Security|US - User Security - Control|
|NIST CSF v1.1||PROTECT (PR)|All users are informed and trained|
|NIST CSF v2.0||PROTECT (PR)|PR.AT-01: Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind|
|ISO27001:2022||6 People controls|Personnel of the organization and relevant interested parties shall receive appropriate information security awareness, education and training and regular updates of the organization's information security policy, topic-specific policies and procedures, as relevant for their job function.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3 Personnel receive security awareness training as follows:  • Upon hire and at least once every 12 months. • Multiple methods of communication are used. • Personnel acknowledge at least once every 12 months that they have read and understood the information security policy and procedures.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.1 Security awareness training includes awareness of threats and vulnerabilities that could impact the security of the CDE, including but not limited to: • Phishing and related attacks.  • Social engineering. Applicability Notes See Requirement 5.4.1 for guidance on the difference between technical and automated controls to detect and protect users from phishing attacks, and this requirement for providing users security awareness training about phishing and social engineering. These are two separate and distinct requirements, and one is not met by implementing controls required by the other one. This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.2 Security awareness training includes awareness about the acceptable use of end-user technologies in accordance with Requirement 12.2.1. Applicability Notes This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|ISO27001:2013||7 Human resource security|Information security awareness, education and training|
|CIS 8.1||Security Awareness and Skills Training||



### US02 - User Security - % of users who have completed Security Awareness training

#### Description

Regular security awareness training will reduce the risk of human error by providing awareness of security issues to your team.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `US02`                                                               |
| **SLO**           | 95.0% - 99.0% |
| **Weight**        | 0.2                                                                    |
| **Resource Type** | user                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||US - User Security|US - User Security - Control|
|NIST CSF v1.1||PROTECT (PR)|All users are informed and trained|
|NIST CSF v2.0||PROTECT (PR)|PR.AT-01: Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind|
|ISO27001:2022||6 People controls|Personnel of the organization and relevant interested parties shall receive appropriate information security awareness, education and training and regular updates of the organization's information security policy, topic-specific policies and procedures, as relevant for their job function.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3 Personnel receive security awareness training as follows:  • Upon hire and at least once every 12 months. • Multiple methods of communication are used. • Personnel acknowledge at least once every 12 months that they have read and understood the information security policy and procedures.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.1 Security awareness training includes awareness of threats and vulnerabilities that could impact the security of the CDE, including but not limited to: • Phishing and related attacks.  • Social engineering. Applicability Notes See Requirement 5.4.1 for guidance on the difference between technical and automated controls to detect and protect users from phishing attacks, and this requirement for providing users security awareness training about phishing and social engineering. These are two separate and distinct requirements, and one is not met by implementing controls required by the other one. This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.2 Security awareness training includes awareness about the acceptable use of end-user technologies in accordance with Requirement 12.2.1. Applicability Notes This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|ISO27001:2013||7 Human resource security|Information security awareness, education and training|
|CIS 8.1||Security Awareness and Skills Training||



### OP01 - Operations - % of hosts detected in the last 30 days

#### Description

Removing old entries from the Vulnerability Management tool ensures consistency and accuracy in the way how vulnerabilities are detected and reported.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `OP01`                                                               |
| **SLO**           | 95.0% - 99.0% |
| **Weight**        | 0.2                                                                    |
| **Resource Type** | device                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||US - User Security|US - User Security - Control|
|NIST CSF v1.1||PROTECT (PR)|All users are informed and trained|
|NIST CSF v2.0||PROTECT (PR)|PR.AT-01: Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind|
|ISO27001:2022||6 People controls|Personnel of the organization and relevant interested parties shall receive appropriate information security awareness, education and training and regular updates of the organization's information security policy, topic-specific policies and procedures, as relevant for their job function.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3 Personnel receive security awareness training as follows:  • Upon hire and at least once every 12 months. • Multiple methods of communication are used. • Personnel acknowledge at least once every 12 months that they have read and understood the information security policy and procedures.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.1 Security awareness training includes awareness of threats and vulnerabilities that could impact the security of the CDE, including but not limited to: • Phishing and related attacks.  • Social engineering. Applicability Notes See Requirement 5.4.1 for guidance on the difference between technical and automated controls to detect and protect users from phishing attacks, and this requirement for providing users security awareness training about phishing and social engineering. These are two separate and distinct requirements, and one is not met by implementing controls required by the other one. This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|PCI DSS v4.0||Requirement 12: Support information security with organizational policies and programs|12.6.3.2 Security awareness training includes awareness about the acceptable use of end-user technologies in accordance with Requirement 12.2.1. Applicability Notes This requirement is a best practice until 31 March 2025, after which it will be required and must be fully considered during a PCI DSS assessment.|
|ISO27001:2013||7 Human resource security|Information security awareness, education and training|
|CIS 8.1||Security Awareness and Skills Training||



### NS01 - Network Security - % of domains with insecure ports

#### Description

Insecure ports have a risk of data exposure if they are not locked down.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `NS01`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | domain                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||NS - Network Security|NS - Network Security - Control|
|CIS 8.1||Data Protection||
|NIST CSF v2.0||IDENTIFY (ID)|ID.AM-03: Representations of the organization's authorized network communication and internal and external network data flows are maintained|
|ISO27001:2022||8 Technological controls|Networks and network devices shall be secured, managed and controlled to protect information in systems and applications.|



### NS02 - Network Security - % of domains with valid TLS certificates

#### Description

Ensuring SSL certificates are valid will ensure that data encryption controls stay in place.

#### Meta Data

| Attribute         | Value                                                                                |
|-------------------|--------------------------------------------------------------------------------------|
| **Metric id**     | `NS02`                                                               |
| **SLO**           | 90.0% - 95.0% |
| **Weight**        | 0.5                                                                    |
| **Resource Type** | domain                                                             |

#### Frameworks

|**Framework**|**Ref**|**Domain**|**Control**|
|--|--|--|--|
|Test-MantelGroup||NS - Network Security|NS - Network Security - Risk|
|CIS 8.1||Data Protection||
|NIST CSF v2.0||PROTECT (PR)|PR.DS-02: The confidentiality, integrity, and availability of data-in-transit are protected|
|ISO27001:2022||8 Technological controls|Rules for the effective use of cryptography, including cryptographic key management, shall be defined and implemented.|


