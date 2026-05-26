# Frequently Asked Questions (FAQ)

Common questions and answers about ZenithOne Explorer.

## General Questions

### What is ZenithOne Explorer?

ZenithOne Explorer is an enterprise-grade platform that brings IBM LinuxONE capabilities to consumer hardware. It provides AI-enhanced workload management, container orchestration, and z/OS subsystem simulation on standard Linux systems.

### Who is ZenithOne Explorer for?

- **Developers**: Learn mainframe concepts on consumer hardware
- **Students**: Study enterprise computing without expensive infrastructure
- **Enterprises**: Prototype and test before deploying to production LinuxONE
- **Researchers**: Experiment with AI-powered workload optimization

### Is ZenithOne Explorer free?

Yes, ZenithOne Explorer is open-source and free to use under the MIT License.

### What hardware do I need?

**Minimum:**
- 4-core CPU
- 8GB RAM
- 20GB storage

**Recommended:**
- 8+ core CPU
- 16GB+ RAM
- 50GB+ SSD storage

### What operating systems are supported?

- Ubuntu 20.04+ (recommended)
- Debian 11+
- Fedora 35+
- Other Linux distributions (may require adjustments)

### Can I run this on Windows or macOS?

Not directly. You'll need:
- **Windows**: WSL2 (Windows Subsystem for Linux)
- **macOS**: Virtual machine (VirtualBox, VMware, Parallels)

## Installation & Setup

### How long does installation take?

Typically 5-10 minutes for a complete installation, depending on your internet speed and system performance.

### Do I need root/sudo access?

Yes, for installing system packages (Podman, Ollama). The application itself can run as a regular user.

### Can I install without internet?

No, you need internet to:
- Download dependencies
- Pull container images
- Download AI models

### What if installation fails?

1. Check the error message
2. Verify system requirements
3. Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
4. Search GitHub issues
5. Create a new issue with details

### How do I update ZenithOne?

```bash
cd zenithone-explorer
git pull origin main
cd backend
pip install -r requirements.txt --upgrade
cd ../cli
npm install
```

## Usage Questions

### How do I start the backend?

```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Can I run the backend in the background?

Yes, use systemd service:
```bash
sudo systemctl start zenithone-backend
```

Or use screen/tmux:
```bash
screen -S zenithone
cd backend && source venv/bin/activate
uvicorn main:app
# Press Ctrl+A, then D to detach
```

### How do I access the UI?

Open your browser and navigate to:
```
http://localhost:8000
```

Default credentials:
- Username: `admin`
- Password: `admin123`

### What's the difference between workload types?

- **Batch**: One-time jobs that run to completion
- **Interactive**: Jobs requiring user interaction
- **Service**: Long-running services (web servers, APIs)
- **Scheduled**: Time-based recurring jobs

### How many workloads can I run simultaneously?

Default limit is 10 concurrent workloads. You can adjust this in configuration:
```bash
# In backend/.env
MAX_CONCURRENT_WORKLOADS=20
```

### Can I schedule workloads for future execution?

Yes, using:
```bash
zenith workload schedule <id> --at "2024-01-01 14:00:00"
```

### What is AI-optimized scheduling?

The AI analyzes:
- Current system load
- Historical patterns
- Resource availability
- Workload priority

Then recommends the optimal execution time.

## Container Questions

### What container runtime does ZenithOne use?

Podman - a daemonless, rootless container engine that's compatible with Docker.

### Can I use Docker instead of Podman?

Not currently. ZenithOne is designed specifically for Podman. Docker support may be added in future versions.

### Where do containers run?

Containers run on your local system using Podman. They're isolated from your host system but share the kernel.

### Can I use my own container images?

Yes! Use any container image from:
- Docker Hub
- Quay.io
- GitHub Container Registry
- Your private registry

### How do I access container logs?

```bash
zenith container logs <container-id>
zenith workload logs <workload-id>
```

### Can containers access my filesystem?

Only if you explicitly mount volumes:
```bash
zenith workload create \
  --volume /host/path:/container/path \
  ...
```

## AI & Ollama Questions

### What AI model does ZenithOne use?

Qwen2.5 by default, running via Ollama. You can use other models by updating the configuration.

### Do I need a GPU?

No, Ollama works on CPU. However, a GPU will improve AI performance.

### How much disk space does the AI model need?

Qwen2.5 requires approximately 4-5GB of disk space.

### Can I use a different AI model?

Yes, install any Ollama-compatible model:
```bash
ollama pull llama2
ollama pull mistral
```

Then update `backend/.env`:
```bash
OLLAMA_MODEL=llama2:latest
```

### What does the AI actually do?

The AI helps with:
- Workload scheduling optimization
- Resource allocation recommendations
- Anomaly detection
- Performance predictions

### Can I disable AI features?

Yes, in `backend/.env`:
```bash
AI_WORKLOAD_OPTIMIZATION=false
AI_RESOURCE_PREDICTION=false
AI_ANOMALY_DETECTION=false
```

## Subsystem Questions

### What are z/OS subsystems?

z/OS subsystems are components of IBM's mainframe operating system. ZenithOne simulates them for learning and testing.

### Are these real z/OS subsystems?

No, they're simulators that mimic the behavior and interfaces of real z/OS subsystems.

### Can I connect real mainframe applications?

No, these are educational simulators, not production-grade implementations.

### What subsystems are available?

- **JES**: Job Entry Subsystem
- **CICS**: Customer Information Control System
- **DB2**: Database Management System
- **TSO**: Time Sharing Option

### How do I start a subsystem?

```bash
zenith subsystem start --name jes
zenith subsystem start --name cics
```

## Performance Questions

### Why is my system slow?

Common causes:
- Too many concurrent workloads
- Insufficient resources
- Heavy AI model usage
- Large container images

Solutions:
- Reduce concurrent workloads
- Increase resource limits
- Use lighter AI models
- Optimize container images

### How do I improve performance?

1. **Increase resources**: More CPU/RAM
2. **Optimize workloads**: Reduce resource usage
3. **Use SSD storage**: Faster disk I/O
4. **Tune configuration**: Adjust worker counts
5. **Monitor metrics**: Identify bottlenecks

### What's the maximum number of containers?

Default limit is 50. Adjust in configuration:
```bash
PODMAN_MAX_CONTAINERS=100
```

### Can I run ZenithOne on a Raspberry Pi?

Technically yes, but not recommended. Minimum 4-core CPU and 8GB RAM are needed for reasonable performance.

## Security Questions

### Is ZenithOne secure?

ZenithOne implements:
- JWT authentication
- Password hashing (bcrypt)
- Input validation
- SQL injection prevention
- XSS protection
- Rate limiting

However, it's designed for development/learning, not production security-critical environments.

### Should I change the default password?

**YES!** Always change default credentials:
```bash
zenith admin user reset-password admin
```

### Can I use HTTPS?

Yes, configure SSL/TLS:
```bash
uvicorn main:app \
  --ssl-keyfile=key.pem \
  --ssl-certfile=cert.pem
```

### How do I secure the API?

1. Change default passwords
2. Use strong JWT secrets
3. Enable rate limiting
4. Use HTTPS in production
5. Implement firewall rules
6. Regular security updates

### Where are credentials stored?

- Backend: Database (hashed passwords)
- CLI: `~/.zenithone/token` (JWT token)
- Never commit credentials to Git

## Troubleshooting

### Backend won't start

Check:
1. Python version (3.14+)
2. Virtual environment activated
3. Dependencies installed
4. Port 8000 available
5. Database initialized

### CLI command not found

```bash
cd cli
npm link
# Add to PATH if needed
export PATH="$PATH:~/.npm-global/bin"
```

### Ollama connection failed

```bash
# Check Ollama service
systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Test connection
curl http://localhost:11434/api/tags
```

### Container won't start

Check:
1. Podman installed and running
2. Image exists (`podman images`)
3. Sufficient resources
4. Container logs for errors

### Database locked error

```bash
# Stop all backend processes
pkill -f uvicorn

# Remove lock file
rm -f backend/data/zenithone.db-journal

# Restart backend
```

## Development Questions

### Can I contribute to ZenithOne?

Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### What programming languages are used?

- **Backend**: Python 3.14 (FastAPI)
- **CLI**: Node.js 22 (JavaScript)
- **UI**: HTML, CSS, JavaScript

### How do I run tests?

```bash
# Backend tests
cd backend
pytest

# CLI tests
cd cli
npm test
```

### How do I add a new feature?

1. Create an issue describing the feature
2. Fork the repository
3. Create a feature branch
4. Implement the feature
5. Add tests
6. Submit a pull request

### Where's the documentation source?

All documentation is in the `docs/` directory in Markdown format.

## Integration Questions

### Can I integrate with CI/CD?

Yes! Use the CLI or REST API in your CI/CD pipelines:
```bash
# In your CI script
zenith auth login --username ci --password $CI_PASSWORD
zenith workload create --file workload.json
zenith workload schedule <id>
```

### Can I use the REST API?

Yes! Full REST API available at:
```
http://localhost:8000/api/v1
```

See [API_REFERENCE.md](../API_REFERENCE.md) for details.

### Can I integrate with monitoring tools?

Yes, export metrics to:
- Prometheus (configure in settings)
- CSV/JSON files
- Custom monitoring solutions via API

### Can I run multiple instances?

Yes, but they need separate:
- Ports
- Databases
- Configuration files

## Licensing & Legal

### What license is ZenithOne under?

MIT License - free to use, modify, and distribute.

### Can I use this commercially?

Yes, the MIT License allows commercial use.

### Do I need to credit ZenithOne?

Not required, but appreciated!

### Is this affiliated with IBM?

No, this is an independent project inspired by IBM LinuxONE.

## Getting Help

### Where can I get help?

1. **Documentation**: Check the docs first
2. **GitHub Issues**: Search existing issues
3. **GitHub Discussions**: Ask questions
4. **Email**: paulmmoore3416@gmail.com

### How do I report a bug?

1. Check if it's already reported
2. Create a GitHub issue
3. Include:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Logs

### How do I request a feature?

Create a GitHub issue with:
- Feature description
- Use case
- Expected behavior
- Alternative solutions considered

### Is there a community?

- GitHub Discussions
- GitHub Issues
- Email support

## Roadmap Questions

### What's planned for future versions?

- Multi-node cluster support
- Enhanced AI capabilities
- More subsystem simulators
- Mobile app
- Cloud integration
- Advanced monitoring

### When is the next release?

Check the [CHANGELOG.md](../../CHANGELOG.md) and GitHub releases for version information.

### Can I suggest features?

Yes! Create a feature request on GitHub Issues.

## Still Have Questions?

If your question isn't answered here:

1. Check the full documentation
2. Search GitHub Issues
3. Ask in GitHub Discussions
4. Contact: paulmmoore3416@gmail.com

## Quick Links

- [Getting Started](GETTING_STARTED.md)
- [First Workload Tutorial](FIRST_WORKLOAD.md)
- [Installation Guide](../INSTALLATION.md)
- [CLI Guide](../CLI_GUIDE.md)
- [API Reference](../API_REFERENCE.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
