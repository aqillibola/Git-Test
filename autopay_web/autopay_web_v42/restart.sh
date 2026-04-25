#!/usr/bin/env bash
systemctl restart autopay.service
systemctl status autopay.service --no-pager -l
