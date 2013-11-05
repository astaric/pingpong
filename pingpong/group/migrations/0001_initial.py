# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'group_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
        ))
        db.send_create_signal(u'group', ['Group'])

        # Adding model 'GroupMember'
        db.create_table(u'group_groupmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['group.Group'])),
            ('place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'group', ['GroupMember'])


    def backwards(self, orm):
        # Deleting model 'Group'
        db.delete_table(u'group_group')

        # Deleting model 'GroupMember'
        db.delete_table(u'group_groupmember')


    models = {
        u'group.group': {
            'Meta': {'object_name': 'Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'})
        },
        u'group.groupmember': {
            'Meta': {'object_name': 'GroupMember'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['group.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']"})
        },
        u'pingpong.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'pingpong.player': {
            'Meta': {'object_name': 'Player'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'players'", 'null': 'True', 'to': u"orm['pingpong.Category']"}),
            'club': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pingpong.table': {
            'Meta': {'object_name': 'Table'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['group']