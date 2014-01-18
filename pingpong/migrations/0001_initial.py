# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
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
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='players', null=True, to=orm['pingpong.Category'])),
        ))
        db.send_create_signal(u'pingpong', ['Player'])

        # Adding model 'Category'
        db.create_table(u'pingpong_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('min_age', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_age', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'pingpong', ['Category'])

        # Adding model 'Table'
        db.create_table(u'pingpong_table', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('short_name', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'pingpong', ['Table'])

        # Adding model 'Match'
        db.create_table(u'pingpong_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Group'], null=True)),
            ('player1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_as_player1', null=True, to=orm['pingpong.Player'])),
            ('player1_score', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('player1_bracket_slot', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['pingpong.BracketSlot'])),
            ('player2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='match_as_player2', null=True, to=orm['pingpong.Player'])),
            ('player2_score', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('player2_bracket_slot', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['pingpong.BracketSlot'])),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='all_matches', null=True, to=orm['pingpong.Table'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'pingpong', ['Match'])

        # Adding model 'Double'
        db.create_table(u'pingpong_double', (
            (u'player_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pingpong.Player'], unique=True, primary_key=True)),
            ('player1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pingpong.Player'])),
            ('player2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['pingpong.Player'])),
        ))
        db.send_create_signal(u'pingpong', ['Double'])

        # Adding model 'Group'
        db.create_table(u'pingpong_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'pingpong', ['Group'])

        # Adding model 'GroupMember'
        db.create_table(u'pingpong_groupmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['pingpong.Group'])),
            ('place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'pingpong', ['GroupMember'])

        # Adding model 'KnownPlayer'
        db.create_table(u'pingpong_knownplayer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('search_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('search_surname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('club', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'pingpong', ['KnownPlayer'])

        # Adding model 'KnownClub'
        db.create_table(u'pingpong_knownclub', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('search_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'pingpong', ['KnownClub'])

        # Adding model 'Bracket'
        db.create_table(u'pingpong_bracket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('levels', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'pingpong', ['Bracket'])

        # Adding model 'BracketSlot'
        db.create_table(u'pingpong_bracketslot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bracket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Bracket'])),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('no_player', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'], null=True, blank=True)),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('match_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('match_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('winner_goes_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='winner_set', null=True, to=orm['pingpong.BracketSlot'])),
            ('loser_goes_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='loser_set', null=True, to=orm['pingpong.BracketSlot'])),
        ))
        db.send_create_signal(u'pingpong', ['BracketSlot'])

        # Adding model 'GroupToBracketTransition'
        db.create_table(u'pingpong_grouptobrackettransition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Group'])),
            ('place', self.gf('django.db.models.fields.IntegerField')()),
            ('slot', self.gf('django.db.models.fields.related.OneToOneField')(related_name='transition', unique=True, to=orm['pingpong.BracketSlot'])),
        ))
        db.send_create_signal(u'pingpong', ['GroupToBracketTransition'])


    def backwards(self, orm):
        # Deleting model 'Player'
        db.delete_table(u'pingpong_player')

        # Deleting model 'Category'
        db.delete_table(u'pingpong_category')

        # Deleting model 'Table'
        db.delete_table(u'pingpong_table')

        # Deleting model 'Match'
        db.delete_table(u'pingpong_match')

        # Deleting model 'Double'
        db.delete_table(u'pingpong_double')

        # Deleting model 'Group'
        db.delete_table(u'pingpong_group')

        # Deleting model 'GroupMember'
        db.delete_table(u'pingpong_groupmember')

        # Deleting model 'KnownPlayer'
        db.delete_table(u'pingpong_knownplayer')

        # Deleting model 'KnownClub'
        db.delete_table(u'pingpong_knownclub')

        # Deleting model 'Bracket'
        db.delete_table(u'pingpong_bracket')

        # Deleting model 'BracketSlot'
        db.delete_table(u'pingpong_bracketslot')

        # Deleting model 'GroupToBracketTransition'
        db.delete_table(u'pingpong_grouptobrackettransition')


    models = {
        u'pingpong.bracket': {
            'Meta': {'object_name': 'Bracket'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pingpong.bracketslot': {
            'Meta': {'object_name': 'BracketSlot'},
            'bracket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Bracket']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'loser_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'loser_set'", 'null': 'True', 'to': u"orm['pingpong.BracketSlot']"}),
            'match_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'match_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'no_player': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'}),
            'winner_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner_set'", 'null': 'True', 'to': u"orm['pingpong.BracketSlot']"})
        },
        u'pingpong.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'pingpong.double': {
            'Meta': {'object_name': 'Double', '_ormbases': [u'pingpong.Player']},
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pingpong.Player']"}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pingpong.Player']"}),
            u'player_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pingpong.Player']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'pingpong.group': {
            'Meta': {'object_name': 'Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'})
        },
        u'pingpong.groupmember': {
            'Meta': {'object_name': 'GroupMember'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': u"orm['pingpong.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']"})
        },
        u'pingpong.grouptobrackettransition': {
            'Meta': {'object_name': 'GroupToBracketTransition'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.IntegerField', [], {}),
            'slot': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'transition'", 'unique': 'True', 'to': u"orm['pingpong.BracketSlot']"})
        },
        u'pingpong.knownclub': {
            'Meta': {'object_name': 'KnownClub'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'search_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pingpong.knownplayer': {
            'Meta': {'object_name': 'KnownPlayer'},
            'club': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'search_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'search_surname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pingpong.match': {
            'Meta': {'object_name': 'Match'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_as_player1'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
            'player1_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['pingpong.BracketSlot']"}),
            'player1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_as_player2'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
            'player2_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['pingpong.BracketSlot']"}),
            'player2_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_matches'", 'null': 'True', 'to': u"orm['pingpong.Table']"})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        }
    }

    complete_apps = ['pingpong']