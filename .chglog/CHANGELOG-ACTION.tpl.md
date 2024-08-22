{{- if .Versions -}}
{{- $latestVersion := index .Versions 0 -}}
<a name="{{ $latestVersion.Tag.Name }}"></a>
## {{ if $latestVersion.Tag.Previous }}[{{ $latestVersion.Tag.Name }}]({{ $.Info.RepositoryURL }}/compare/{{ $latestVersion.Tag.Previous.Name }}...{{ $latestVersion.Tag.Name }}){{ else }}{{ $latestVersion.Tag.Name }}{{ end }} ({{ datetime "2006-01-02" $latestVersion.Tag.Date }})

{{ range $latestVersion.CommitGroups -}}
### {{ .Title }}

{{ range .Commits -}}
* {{ if .Scope }}**{{ .Scope }}:** {{ end }}{{ .Subject }}
{{ end }}
{{ end -}}

{{- if $latestVersion.NoteGroups -}}
{{ range $latestVersion.NoteGroups -}}
### {{ .Title }}

{{ range .Notes }}
{{ .Body }}
{{ end }}
{{ end -}}
{{ end -}}
{{ end -}}
