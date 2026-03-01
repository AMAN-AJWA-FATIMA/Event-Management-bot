


from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Event, EventCategory, Role, Registration


# ─── Admin Site Branding ───────────────────────────────────────
admin.site.site_header  = "⚡ Event Bot Admin"
admin.site.site_title   = "Event Bot"
admin.site.index_title  = "Control Panel"


# ─── EventCategory ────────────────────────────────────────────
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display  = ('color_preview', 'name', 'slug', 'event_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block; width:14px; height:14px; '
            'border-radius:4px; background:{}; '
            'box-shadow:0 0 6px {}44; vertical-align:middle;"></span>',
            obj.color, obj.color
        )
    color_preview.short_description = ''

    def event_count(self, obj):
        count = obj.events.count()
        return format_html(
            '<span style="background:rgba(99,102,241,.12); border:1px solid rgba(99,102,241,.25); '
            'color:#a5b4fc; padding:2px 10px; border-radius:999px; font-size:.78rem; font-weight:600;">'
            '{}</span>', count
        )
    event_count.short_description = 'Events'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(event_count=Count('events'))


# ─── Role Inline (inside Event) ───────────────────────────────
class RoleInline(admin.TabularInline):
    model   = Role
    extra   = 1
    fields  = ('name', 'max_capacity')
    verbose_name = "Role"
    verbose_name_plural = "Roles / Capacity Slots"


# ─── Event ────────────────────────────────────────────────────
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ('name', 'status_badge', 'category_badge', 'start_date',
                     'end_date', 'capacity_bar', 'created_by', 'created_at')
    list_filter   = ('status', 'category', 'start_date')
    search_fields = ('name', 'description', 'created_by__username')
    ordering      = ('-created_at',)
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at',)
    inlines       = [RoleInline]

    fieldsets = (
        ('Event Info', {
            'fields': ('name', 'description', 'category', 'status')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date')
        }),
        ('Capacity', {
            'fields': ('max_participants',)
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'published':  ('#34d399', '#064e3b', '#6ee7b7'),
            'draft':      ('#94a3b8', '#1e293b', '#cbd5e1'),
            'cancelled':  ('#f87171', '#7f1d1d', '#fca5a5'),
            'completed':  ('#818cf8', '#1e1b4b', '#c7d2fe'),
        }
        bg, border_dark, text = colors.get(obj.status, ('#94a3b8', '#1e293b', '#cbd5e1'))
        return format_html(
            '<span style="background:{}22; border:1px solid {}44; color:{}; '
            'padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:600; '
            'text-transform:uppercase; letter-spacing:.06em;">{}</span>',
            bg, bg, text, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def category_badge(self, obj):
        if not obj.category:
            return format_html('<span style="color:#4a5568;">—</span>')
        return format_html(
            '<span style="background:{}22; color:{}; padding:3px 10px; '
            'border-radius:999px; font-size:.75rem; font-weight:600;">{}</span>',
            obj.category.color, obj.category.color, obj.category.name
        )
    category_badge.short_description = 'Category'

    def capacity_bar(self, obj):
        total   = obj.max_participants
        current = obj.registrations.count()
        pct     = min(int((current / total) * 100), 100) if total else 0
        color   = '#34d399' if pct < 60 else '#fbbf24' if pct < 90 else '#f87171'
        return format_html(
            '<div style="display:flex; align-items:center; gap:8px; min-width:130px;">'
            '<div style="flex:1; height:6px; background:rgba(255,255,255,.08); border-radius:3px; overflow:hidden;">'
            '<div style="width:{}%; height:100%; background:{}; border-radius:3px; transition:width .3s;"></div>'
            '</div>'
            '<span style="font-size:.78rem; color:#8b9ab5; white-space:nowrap;">{}/{}</span>'
            '</div>',
            pct, color, current, total
        )
    capacity_bar.short_description = 'Capacity'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'created_by')


# ─── Role ─────────────────────────────────────────────────────
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'event', 'capacity_display', 'registrations_count')
    list_filter   = ('event',)
    search_fields = ('name', 'event__name')
    ordering      = ('event__name', 'name')

    def capacity_display(self, obj):
        if obj.max_capacity is None:
            return format_html(
                '<span style="color:#6b7a99; font-size:.8rem;">∞ Unlimited</span>'
            )
        return format_html(
            '<span style="background:rgba(99,102,241,.12); color:#a5b4fc; '
            'padding:2px 10px; border-radius:999px; font-size:.78rem; font-weight:600;">'
            '{} slots</span>', obj.max_capacity
        )
    capacity_display.short_description = 'Capacity'

    def registrations_count(self, obj):
        count = obj.registrations.count()
        return format_html(
            '<span style="color:#8b9ab5; font-size:.84rem;">{} registered</span>', count
        )
    registrations_count.short_description = 'Registrations'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event').annotate(
            reg_count=Count('registrations')
        )


# ─── Registration ─────────────────────────────────────────────
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display  = ('user_display', 'event_display', 'role_display',
                     'registered_at')
    list_filter   = ('event', 'role', 'registered_at')
    search_fields = ('user__username', 'user__email', 'event__name')
    ordering      = ('-registered_at',)
    readonly_fields = ('registered_at',)
    date_hierarchy  = 'registered_at'

    def user_display(self, obj):
        return format_html(
            '<span style="display:flex; align-items:center; gap:8px;">'
            '<span style="width:28px; height:28px; border-radius:50%; '
            'background:linear-gradient(135deg,#6366f1,#7c3aed); '
            'display:inline-flex; align-items:center; justify-content:center; '
            'color:#fff; font-size:.72rem; font-weight:700; flex-shrink:0;">{}</span>'
            '<span style="font-weight:500; color:#c9d1e0;">{}</span>'
            '</span>',
            obj.user.username[0].upper(), obj.user.username
        )
    user_display.short_description = 'User'

    def event_display(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/" style="color:#818cf8; '
            'font-weight:500; text-decoration:none;">{}</a>',
            obj.event.pk, obj.event.name
        )
    event_display.short_description = 'Event'

    def role_display(self, obj):
        if not obj.role:
            return format_html('<span style="color:#4a5568;">No role</span>')
        return format_html(
            '<span style="background:rgba(45,212,191,.10); border:1px solid rgba(45,212,191,.2); '
            'color:#5eead4; padding:2px 9px; border-radius:999px; font-size:.75rem; font-weight:600;">'
            '{}</span>', obj.role.name
        )
    role_display.short_description = 'Role'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event', 'role')