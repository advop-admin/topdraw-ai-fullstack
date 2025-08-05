# Topsdraw Blueprint Generator

An AI-powered business blueprint generator for UAE market entry. Generate comprehensive business plans, timelines, and recommendations tailored to your business type and requirements.

## 🚀 One-Line Installation

```bash
curl -fsSL https://raw.githubusercontent.com/advop-admin/topdraw-ai-fullstack/main/install.sh | sudo bash
```

## ✨ Features

- 🎯 Business plan generation
- 💡 Creative recommendations
- 📊 Budget planning
- 🗓 Timeline creation
- 🤝 Agency matching
- 📈 Market analysis

## 🛠 System Requirements

- Ubuntu 20.04+ / Debian 11+
- 4GB RAM minimum
- 20GB free disk space
- Internet connection

## 🔑 Configuration

After installation:

1. Set your Gemini API key:
```bash
cd /opt/topsdraw
nano .env
# Add your GEMINI_API_KEY
```

2. Restart services:
```bash
docker compose restart
```

## 📱 Usage

Access the application at:
- Frontend: http://localhost:3001
- API: http://localhost:8003

## 🔄 Updates

To update to the latest version:
```bash
cd /opt/topsdraw
git pull
docker compose up -d --build
```

## 🔍 Monitoring

View logs:
```bash
cd /opt/topsdraw
docker compose logs -f
```

## ❌ Uninstallation

To remove completely:
```bash
cd /opt/topsdraw
docker compose down -v
cd ..
sudo rm -rf /opt/topsdraw
```

## 🔒 Security Notes

- Change default database passwords in .env
- Set up SSL if exposing to internet
- Keep your Gemini API key secure
- Regular updates recommended

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 💬 Support

- Create an issue for bug reports
- Join our community for discussions
- Check documentation for guides