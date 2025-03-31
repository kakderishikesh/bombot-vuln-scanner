# bombo-vuln-scanner

# 🤖 BomBot – Vulnerability Scanner for SBOMs using OSV

**BomBot** is a simple, smart chatbot that takes a Software Bill of Materials (SBOM) in SPDX JSON format, scans it against the [OSV (Open Source Vulnerabilities) database](https://osv.dev), and returns a report of known vulnerabilities for each software package.

> Designed for security analysts, developers, and open-source maintainers who want a quick and effective way to check for vulnerabilities in their software dependencies.

---

## 🔍 Features

- 📥 Accepts SPDX-formatted SBOMs (JSON)
- 🔐 Queries the OSV API to detect known vulnerabilities
- 📋 Generates a clear, actionable report listing affected packages
- 🤖 Packaged as a chatbot (CLI or web-based) for ease of use
- 💡 Future-ready: room for CI/CD integration, notifications, or remediation suggestions

---

## 📁 Project Structure

```bash
BomBot/
├── README.md              # This file
├── LICENSE                # License information
├── .gitignore             # Ignore OS, IDE, and notebook files
├── data/                  # Sample SBOM files (SPDX JSON)
├── results/               # Sample vulnerability reports
├── images/                # Screenshots or diagrams
├── docs/                  # Project notes, references, future roadmap

