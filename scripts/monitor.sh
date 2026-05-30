#!/bin/bash

VPS_IP="187.127.156.138"
DOMAIN="mudra.kibm.in"

echo "📊 Mudra Monitoring Dashboard"
echo "=============================="
echo "Timestamp: $(date)"
echo ""

echo "🐳 Container Status:"
ssh root@$VPS_IP "docker ps --filter name=mudra"

echo ""
echo "📈 System Resources:"
ssh root@$VPS_IP "free -h && df -h /opt/mudra"

echo ""
echo "🌐 SSL Certificate Status:"
curl -vI https://$DOMAIN 2>&1 | grep "expire date"

echo ""
echo "📊 Application Logs (last 10 lines):"
ssh root@$VPS_IP "docker logs --tail 10 mudra-app"
