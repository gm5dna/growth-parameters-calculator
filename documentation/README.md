# Documentation Index

Welcome to the Growth Parameters Calculator documentation. This folder contains comprehensive guides covering all aspects of the application.

## Documentation Structure

### User Documentation

- **[Features Guide](FEATURES.md)** - Detailed description of all application features
  - Core calculations (age, weight, height, BMI, OFC)
  - Interactive growth charts
  - Growth references (UK-WHO, CDC, Turner, Trisomy 21)
  - Data quality and validation
  - GH dose calculator
  - Gestational age correction
  - Body surface area methods
  - User interface features

- **[User Guide](USER_GUIDE.md)** - Step-by-step usage instructions
  - Getting started
  - Basic workflow
  - Detailed input instructions
  - Understanding results
  - Using growth charts
  - Advanced features
  - Tips and best practices
  - Troubleshooting

### Technical Documentation

- **[Technical Documentation](TECHNICAL.md)** - Architecture and implementation
  - System architecture
  - Backend implementation (Flask, Python modules)
  - Frontend implementation (JavaScript, CSS)
  - Data flow
  - Security measures
  - Performance optimization
  - Deployment guide

- **[Project Design Document](PROJECT_DESIGN.md)** - Design decisions and architecture
  - Project vision and principles
  - High-level architecture
  - Module responsibilities
  - Feature specifications
  - API reference
  - Testing strategy
  - Decision log

### Development Documentation

- **[Recent Improvements](IMPROVEMENTS_SUMMARY.md)** - Latest enhancements
  - High priority improvements completed
  - Medium priority improvements completed
  - Code quality improvements
  - Testing instructions
  - Production deployment notes

- **[Future Improvements](FUTURE_IMPROVEMENTS.md)** - Feature backlog and roadmap
  - Completed features
  - Planned enhancements by category
  - Priority rankings
  - Implementation notes

### Feature Plans and Reports

- **[feature-plans/](feature-plans/)** - Feature implementation plans
  - Copy results feature plan
  - Feature history and evolution

- **[test-reports/](test-reports/)** - Testing documentation
  - Mobile responsiveness test report
  - Feature validation reports

## Quick Links

### For Users
- **New to the app?** Start with the [User Guide](USER_GUIDE.md#getting-started)
- **Want to know what it does?** Check [Features Guide](FEATURES.md#core-calculations)
- **Need help?** See [Troubleshooting](USER_GUIDE.md#troubleshooting)

### For Developers
- **Understanding the code?** Read [Technical Documentation](TECHNICAL.md#system-architecture)
- **Want to contribute?** See the main [README](../README.md#contributing)
- **Running tests?** Check [IMPROVEMENTS_SUMMARY](IMPROVEMENTS_SUMMARY.md#testing-instructions)

### For Clinicians
- **Clinical features**: [Data Quality and Safety](FEATURES.md#data-quality-and-safety)
- **Interpreting results**: [Understanding Results](USER_GUIDE.md#understanding-results)
- **Growth charts**: [Using Growth Charts](USER_GUIDE.md#using-growth-charts)

## Document Overview

### FEATURES.md (Comprehensive Feature Documentation)
**Length**: ~600 lines
**Audience**: Users, clinicians, developers
**Purpose**: Complete reference for all application features

**Sections**:
- Core Calculations (age, measurements, velocity, MPH)
- Interactive Growth Charts (visual features, interactions)
- Growth References (UK-WHO, CDC, Turner, Trisomy 21)
- Data Quality and Safety (SDS validation, warnings)
- GH Dose Calculator (dosing, increments, equivalents)
- Gestational Age Correction (eligibility, method, visualization)
- Body Surface Area Methods (Boyd, cBNF)
- User Interface Features (responsive design, PWA, modes)

### USER_GUIDE.md (Step-by-Step Instructions)
**Length**: ~700 lines
**Audience**: End users, clinicians
**Purpose**: Practical guide to using the application

**Sections**:
- Getting Started (accessing, first-time setup)
- Basic Workflow (3-step quick start)
- Detailed Instructions (every input field explained)
- Understanding Results (interpreting output)
- Using Growth Charts (chart features, interactions)
- Advanced Features (mode toggle, auto-save)
- Tips and Best Practices (measurement tips, interpretation)
- Troubleshooting (common errors, solutions)

### TECHNICAL.md (Architecture and Implementation)
**Length**: ~800 lines
**Audience**: Developers, system administrators
**Purpose**: Technical reference for developers

**Sections**:
- System Architecture (components, design principles)
- Backend Implementation (Flask, modules, dependencies)
- Frontend Implementation (JavaScript, CSS, charts)
- Data Flow (request/response cycles)
- Security (validation, rate limiting, data handling)
- Performance (optimization, PWA, caching)
- Deployment (production setup, scaling)

### IMPROVEMENTS_SUMMARY.md (Recent Changes)
**Length**: ~500 lines
**Audience**: Developers, project maintainers
**Purpose**: Document recent code improvements

**Sections**:
- Completed Improvements (high and medium priority)
- Files Created/Modified (detailed list)
- Code Quality Improvements (architecture, testing)
- Testing Instructions (pytest commands)
- Production Deployment Notes (checklist)

## How to Use This Documentation

### For First-Time Users

1. **Read the main [README](../README.md)** - Quick overview and installation
2. **Follow [User Guide > Getting Started](USER_GUIDE.md#getting-started)** - First steps
3. **Try [User Guide > Basic Workflow](USER_GUIDE.md#basic-workflow)** - Simple calculation
4. **Explore [Features Guide](FEATURES.md)** - Learn all features

### For Developers

1. **Read [Technical Documentation > Architecture](TECHNICAL.md#system-architecture)** - System overview
2. **Review [IMPROVEMENTS_SUMMARY](IMPROVEMENTS_SUMMARY.md)** - Recent changes
3. **Study [Technical Documentation > Implementation](TECHNICAL.md#backend-implementation)** - Code structure
4. **Check [Testing Instructions](IMPROVEMENTS_SUMMARY.md#testing-instructions)** - Run tests

### For Clinicians

1. **Read [Features Guide > Data Quality](FEATURES.md#data-quality-and-safety)** - Safety features
2. **Learn [User Guide > Understanding Results](USER_GUIDE.md#understanding-results)** - Interpret output
3. **Practice [User Guide > Workflow](USER_GUIDE.md#basic-workflow)** - Try calculations
4. **Master [Features Guide > Growth Charts](FEATURES.md#interactive-growth-charts)** - Visualization

### For System Administrators

1. **Study [Technical Documentation > Security](TECHNICAL.md#security)** - Security measures
2. **Review [Technical Documentation > Deployment](TECHNICAL.md#deployment)** - Setup guide
3. **Check [Technical Documentation > Performance](TECHNICAL.md#performance)** - Optimization
4. **Read [IMPROVEMENTS_SUMMARY > Deployment Notes](IMPROVEMENTS_SUMMARY.md#production-deployment-notes)** - Checklist

## Additional Resources

### External Documentation

- **rcpchgrowth Library**: [https://growth.rcpch.ac.uk/developer/rcpchgrowth/](https://growth.rcpch.ac.uk/developer/rcpchgrowth/)
- **Flask Documentation**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- **Chart.js Documentation**: [https://www.chartjs.org/docs/](https://www.chartjs.org/docs/)
- **pytest Documentation**: [https://docs.pytest.org/](https://docs.pytest.org/)

### Project Links

- **GitHub Repository**: [https://github.com/gm5dna/growth-parameters-calculator](https://github.com/gm5dna/growth-parameters-calculator)
- **Live Application**: [https://growth-parameters-calculator.onrender.com](https://growth-parameters-calculator.onrender.com)
- **Issue Tracker**: [https://github.com/gm5dna/growth-parameters-calculator/issues](https://github.com/gm5dna/growth-parameters-calculator/issues)
- **Discussions**: [https://github.com/gm5dna/growth-parameters-calculator/discussions](https://github.com/gm5dna/growth-parameters-calculator/discussions)

## Document Maintenance

### Last Updated
January 2026

### Version
All documentation reflects the current state of the application after the high and medium priority improvements were completed.

### Contributing to Documentation

If you find errors or want to improve documentation:

1. **Small fixes**: Submit pull request with changes
2. **Large changes**: Open issue first to discuss
3. **New sections**: Coordinate with maintainers
4. **Questions**: Use GitHub Discussions

### Documentation Standards

- **Clear language**: Write for target audience
- **Examples**: Include practical examples
- **Code blocks**: Use syntax highlighting
- **Links**: Keep internal links relative
- **Images**: Store in `docs/images/` if needed
- **Updates**: Keep in sync with code changes

## Need Help?

### For Documentation Issues

- **Unclear instructions**: Open issue with "documentation" label
- **Missing information**: Suggest additions via discussion
- **Errors**: Submit pull request with corrections
- **Questions**: Ask in GitHub Discussions

### For Application Issues

- **Bug reports**: Use GitHub Issues
- **Feature requests**: Use GitHub Discussions
- **Security concerns**: Email maintainer directly
- **General questions**: GitHub Discussions

## License and Attribution

This documentation is part of the Growth Parameters Calculator open source project.

**Created by**: Stuart ([@gm5dna](https://github.com/gm5dna))
**Powered by**: [rcpchgrowth library](https://growth.rcpch.ac.uk/developer/rcpchgrowth/) from RCPCH
**License**: See main [README](../README.md#license)

---

**Remember**: This tool is for educational and research purposes only. Always verify calculations independently before any clinical use.
