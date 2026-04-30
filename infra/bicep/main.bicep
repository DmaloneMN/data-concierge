// main.bicep - Entry point for all infrastructure deployments
// TODO: Wire up modules for AI Foundry, Container Apps, Key Vault, APIM, Monitor

targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string

// TODO: Add module references
