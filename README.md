# Coldpool

Coldpool is a Linux self-hosted web application for managing **cold backup storage** across a pool of offline hard disks.

It is designed for people who keep backup artifacts on **new, used, or heavily used disks**, especially when those disks are inexpensive, mixed in size, or of uncertain long-term reliability.

## Purpose

The goal of Coldpool is to provide a **centralized interface** to organize and manage backup artifacts that are stored on offline disks.

In Coldpool, an **artifact** is a backup unit that must be preserved on cold storage, such as:
- `.zip` archives
- `.7z` archives
- `.img` disk images

The system helps users decide **where artifacts should be stored** based on disk capacity and disk health.

## Main Idea

Cold storage is useful, but offline disks are inconvenient to manage manually over time.

Coldpool helps by:
- tracking available hard disks
- tracking disk size and storage usage
- recording a disk health value
- assigning more important artifacts to healthier disks
- providing a central web interface to review and manage the backup pool

Users can periodically open the web interface, connect disks through USB-to-SATA adapters, and move artifacts between disks as needed.

## Why Disk Health Matters

A disk kept in cold storage may fail months or years later, and its future reliability is never guaranteed.

However, in practice, some disks are likely to be more trustworthy than others. For example:
- new or certified brand disks may be more reliable
- heavily used disks may be less reliable
- off-brand or unknown-source disks may deserve lower trust
- disks showing SMART errors should be treated with extra caution

For this reason, Coldpool uses a **health parameter** so that higher-priority artifacts can be placed on higher-confidence disks.

## Ideal Use Case

Coldpool is especially useful for users who:
- maintain offline backups
- have access to cheap second-hand hard disks
- want to reuse disks of different sizes and conditions
- prefer a lightweight self-hosted interface instead of ad hoc manual tracking

## Summary

Coldpool is a practical tool for managing offline backup artifacts across many hard disks, helping users make better storage decisions based on **capacity**, **health**, and **artifact importance**.

## Installation

Coldpool is installed on a Linux machine from a release archive.

A release archive contains:
- `install.sh`
- the Coldpool backend package
- the built frontend files
- example configuration files
- a `systemd` service file
- a `VERSION` file

A typical release file looks like:

```text
coldpool-vX.Y.Z-linux-x86_64.tar.gz