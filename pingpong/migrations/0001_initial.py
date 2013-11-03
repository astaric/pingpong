# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Player'
        db.create_table(u'pingpong_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('club', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'], null=True, blank=True)),
        ))
        db.send_create_signal(u'pingpong', ['Player'])

        # Adding model 'Category'
        db.create_table(u'pingpong_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')()),
            ('min_age', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_age', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pingpong', ['Category'])


    def backwards(self, orm):
        # Deleting model 'Player'
        db.delete_table(u'pingpong_player')

        # Deleting model 'Category'
        db.delete_table(u'pingpong_category')


    models = {
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']", 'null': 'True', 'blank': 'True'}),
            'club': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pingpong']