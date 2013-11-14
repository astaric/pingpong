# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Bracket'
        db.create_table(u'bracket_bracket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('levels', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'bracket', ['Bracket'])

        # Adding model 'BracketSlot'
        db.create_table(u'bracket_bracketslot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bracket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bracket.Bracket'])),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('no_player', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'], null=True, blank=True)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('match_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('match_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('winner_goes_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='winner_set', null=True, to=orm['bracket.BracketSlot'])),
            ('loser_goes_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='loser_set', null=True, to=orm['bracket.BracketSlot'])),
        ))
        db.send_create_signal(u'bracket', ['BracketSlot'])

        # Adding model 'GroupToBracketTransition'
        db.create_table(u'bracket_grouptobrackettransition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['group.Group'])),
            ('place', self.gf('django.db.models.fields.IntegerField')()),
            ('slot', self.gf('django.db.models.fields.related.OneToOneField')(related_name='transition', unique=True, to=orm['bracket.BracketSlot'])),
        ))
        db.send_create_signal(u'bracket', ['GroupToBracketTransition'])

        # Adding unique constraint on 'GroupToBracketTransition', fields ['group', 'place']
        db.create_unique(u'bracket_grouptobrackettransition', ['group_id', 'place'])

        # Adding unique constraint on 'GroupToBracketTransition', fields ['slot']
        db.create_unique(u'bracket_grouptobrackettransition', ['slot_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'GroupToBracketTransition', fields ['slot']
        db.delete_unique(u'bracket_grouptobrackettransition', ['slot_id'])

        # Removing unique constraint on 'GroupToBracketTransition', fields ['group', 'place']
        db.delete_unique(u'bracket_grouptobrackettransition', ['group_id', 'place'])

        # Deleting model 'Bracket'
        db.delete_table(u'bracket_bracket')

        # Deleting model 'BracketSlot'
        db.delete_table(u'bracket_bracketslot')

        # Deleting model 'GroupToBracketTransition'
        db.delete_table(u'bracket_grouptobrackettransition')


    models = {
        u'bracket.bracket': {
            'Meta': {'object_name': 'Bracket'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'bracket.bracketslot': {
            'Meta': {'object_name': 'BracketSlot'},
            'bracket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bracket.Bracket']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'loser_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'loser_set'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"}),
            'match_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'match_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'no_player': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'}),
            'winner_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner_set'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"})
        },
        u'bracket.grouptobrackettransition': {
            'Meta': {'unique_together': "(('group', 'place'), ('slot',))", 'object_name': 'GroupToBracketTransition'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['group.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.IntegerField', [], {}),
            'slot': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'transition'", 'unique': 'True', 'to': u"orm['bracket.BracketSlot']"})
        },
        u'group.group': {
            'Meta': {'object_name': 'Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'})
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

    complete_apps = ['bracket']