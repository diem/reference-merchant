{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "diem-reference-merchant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "diem-reference-merchant.fullname" -}}
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
{{- define "diem-reference-merchant.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "diem-reference-merchant.labels" -}}
helm.sh/chart: {{ include "diem-reference-merchant.chart" . }}
{{ include "diem-reference-merchant.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "diem-reference-merchant.selectorLabels" -}}
app.kubernetes.io/name: {{ include "diem-reference-merchant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "diem-reference-merchant.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "diem-reference-merchant.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Create the payment VASP URL
*/}}
{{- define "diem-reference-merchant.vaspUrl" -}}
http://{{ include "diem-reference-merchant.fullname" . }}-vasp:{{ .Values.service.port }}
{{- end }}

{{- define "diem-reference-merchant.peripherals.redis.url" -}}
{{- if .Values.peripherals.redis.create }}
{{- (include "diem-reference-merchant.fullname" .) }}-redis
{{- else }}
{{ .Values.peripherals.redis.host }}
{{- end }}
{{- end }}

{{- define "diem-reference-merchant.peripherals.database.url" -}}
{{- if .Values.peripherals.database.create }}
{{- $host := printf "%s-db" (include "diem-reference-merchant.fullname" .) }}
{{- with .Values.peripherals.database }}
{{- .protocol }}://{{ .username }}:{{ .password }}@{{ $host }}:{{ .port }}/{{ .dbName }}
{{- end }}
{{- else }}
{{- .Values.peripherals.database.host }}
{{- end }}
{{- end }}

{{- define "diem-reference-merchant.peripherals.database.liquidityUrl" -}}
{{- if .Values.peripherals.database.create }}
{{- $host := printf "%s-db" (include "diem-reference-merchant.fullname" .) }}
{{- with .Values.peripherals.database }}
{{- .protocol }}://{{ .username }}:{{ .password }}@{{ $host }}:{{ .port }}/{{ .liquidityDbName }}
{{- end }}
{{- else }}
{{- .Values.peripherals.database.host }}
{{- end }}
{{- end }}
