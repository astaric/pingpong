# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Group'
        db.delete_table(u'group_group')

        # Deleting model 'GroupMember'
        db.delete_table(u'group_groupmember')


    def backwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'group_group', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'group', ['Group'])

        # Adding model 'GroupMember'
        db.create_table(u'group_groupmember', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['group.Group'])),
            ('leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'])),
            ('place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'group', ['GroupMember'])


    models = {
        
    }

    complete_apps = ['group']