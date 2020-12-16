{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "reference-merchant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "reference-merchant.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "reference-merchant.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "reference-merchant.labels" -}}
helm.sh/chart: {{ include "reference-merchant.chart" . }}
{{ include "reference-merchant.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "reference-merchant.selectorLabels" -}}
app.kubernetes.io/name: {{ include "reference-merchant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "reference-merchant.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "reference-merchant.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Create the payment VASP URL
*/}}
{{- define "reference-merchant.vaspUrl" -}}
http://{{ include "reference-merchant.fullname" . }}-vasp:{{ .Values.service.port }}
{{- end }}

{{- define "reference-merchant.peripherals.redis.url" -}}
{{- if .Values.peripherals.redis.create }}
{{- (include "reference-merchant.fullname" .) }}-redis
{{- else }}
{{ .Values.peripherals.redis.host }}
{{- end }}
{{- end }}

{{- define "reference-merchant.peripherals.database.url" -}}
{{- if .Values.peripherals.database.create }}
{{- $host := printf "%s-db" (include "reference-merchant.fullname" .) }}
{{- with .Values.peripherals.database }}
{{- .protocol }}://{{ .username }}:{{ .password }}@{{ $host }}:{{ .port }}/{{ .dbName }}
{{- end }}
{{- else }}
{{- .Values.peripherals.database.host }}
{{- end }}
{{- end }}

{{- define "reference-merchant.peripherals.database.liquidityUrl" -}}
{{- if .Values.peripherals.database.create }}
{{- $host := printf "%s-db" (include "reference-merchant.fullname" .) }}
{{- with .Values.peripherals.database }}
{{- .protocol }}://{{ .username }}:{{ .password }}@{{ $host }}:{{ .port }}/{{ .liquidityDbName }}
{{- end }}
{{- else }}
{{- .Values.peripherals.database.host }}
{{- end }}
{{- end }}
