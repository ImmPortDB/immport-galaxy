<%!
#This is a hack, we should restructure templates to avoid this.
def inherit(context):
    if context.get('trans').webapp.name == 'galaxy' and context.get( 'use_panels', True ):
        return '/webapps/galaxy/base_panels.mako'
    elif context.get('trans').webapp.name == 'tool_shed' and context.get( 'use_panels', True ):
        return '/webapps/tool_shed/base_panels.mako'
    else:
        return '/base.mako'
%>

<%inherit file="${inherit(context)}"/>

<%def name="init()">
<%
    self.has_left_panel=False
    self.has_right_panel=False
    self.active_view=active_view
    self.message_box_visible=False
%>
</%def>

<%namespace file="/message.mako" import="render_msg" />

<%def name="center_panel()">
    ${body()}
</%def>

<%def name="body()">

    %if redirect_url:
        <script type="text/javascript">  
            top.location.href = '${redirect_url | h}';
        </script>
    %endif

    %if context.get('use_panels'):
        <div style="margin: 1em;">
    %else:
        <div>
    %endif

    %if message:
        ${render_msg( message, status )}
    %endif

    %if not trans.user:

        ${render_login_form()}

        <br/>
        %if hasattr(trans.app.config, 'enable_oidc') and trans.app.config.enable_oidc:
            <br/>
            ${render_oidc_form()}
        %endif

        %if trans.app.config.enable_openid:
            <br/>
            ${render_openid_form( redirect, False, openid_providers )}
        %endif

        %if trans.app.config.get( 'terms_url', None ) is not None:
            <br/>
            <!--p>
                <a href="${trans.app.config.get('terms_url', None)}">Terms and Conditions for use of this service</a>
            </p-->
        %endif

    %endif

    </div>

</%def>

<%def name="render_login_form( form_action=None )">

    <%
        if form_action is None:
            form_action = h.url_for( controller='user', action='login', use_panels=use_panels )
    %>

    <script type="text/javascript">
	$(document).ready(function() {

	    $('#login_check').on("click", function(){
		$('#loginIG').prop('disabled', !this.checked);   
	    });
	    
	
	});
    </script>

    %if header:
        ${header}
    %endif
    <div id="loginForm" class="toolForm center-login" style="border:none;">
        <!--div class="toolFormTitle">Login</div-->
        <form name="login" id="login" action="${form_action}" method="post" >
            <input type="hidden" name="session_csrf_token" value="${trans.session_csrf_token}" />
 	    <div class="text-center">
		<br /><br /><p>
		    <img class="main-site-logo" src="/static/images/flowtools/home/immportgalaxy_green_sharp.png" alt="ImmPort Galaxy logo" style="height:130px;"/>
		</p>
	    </div>
   	    <br />
    	    <div>
		<p>Please enter your credentials to access ImmPort Galaxy resources.</p>
		<p style="font-size:12px">
		<i>Note these are specific to ImmPort Galaxy and do not grant access to other ImmPort resources or Galaxy instances.</i> </p>
	    </div>
	    <br />
            <div class="form-row">
                <!--label>Username / Email Address:</label-->
                <input type="text" name="login" value="${login or ''| h}" size="40" placeholder="User Name / Email Address" class="login-box" style="width:100%;"/>
                <input type="hidden" name="redirect" value="${redirect | h}" size="40"/>
            </div>
            <div class="form-row">
                <!--label>Password:</label-->
                <input type="password" name="password" value="" size="40" placeholder="Password" class="login-box" style="width:100%;"/>
                <!--div class="toolParamHelp" style="clear: both;">
                    <a href="${h.url_for( controller='user', action='reset_password', use_panels=use_panels )}">Forgot password? Reset here</a>
                </div-->
            </div>
	    <br />
	    <div style="text-align: justify;">
		By checking the <strong>"I Accept"</strong> box below,
    	        you confirm that you have read and accept
                all the terms and conditions without limitation of the
            	<strong><a target="_blank" href="http://www.immport.org/agreement">User Agreement</a>
                for the NIAID Immunology Database and Analysis Portal.</strong>
            </div>
            <br />
	    <div class="checkbox-inline">
                <label> <input id="login_check" type="checkbox" style="margin-top:4px;"/>&nbsp;&nbsp;<strong>I Accept</strong>
                </label>
            </div>	
	    <div class="row">
                <div class="form-row col-sm-5" style="margin-left:7px;">
                    <input type="submit" id="loginIG" name="login_button" value="Log in" class="btn-primary" disabled="true" style="font-size:14px;"/>
	        </div>
		
		<div class="forgot-pw col-sm-5">
                    <div class="toolParamHelp" style="float:right;">
                        <a href="${h.url_for( controller='user', action='reset_password', use_panels=use_panels )}">Forgot password?<br /> Reset here</a>
                    </div>
		</div>
            </div>
        </form>
    </div>
</%def>

<%def name="render_oidc_form( form_action=None )">

    <%
        if form_action is None:
            form_action = h.url_for( controller='authnz', action='login', provider='Google' )
    %>

    %if header:
        ${header}
    %endif
    <div class="toolForm">
        <div class="toolFormTitle">OR</div>
        <form name="oidc" id="oidc" action="${form_action}" method="post" >
            <div class="form-row">
                <input type="submit" value="Login with Google"/>
            </div>
        </form>
    </div>

</%def>

<%def name="render_openid_form( redirect, auto_associate, openid_providers )">
    <div class="toolForm">
        <div class="toolFormTitle">OpenID Login</div>
        <form name="openid" id="openid" action="${h.url_for( controller='user', action='openid_auth' )}" method="post" target="_parent" >
            <div class="form-row">
                <label>OpenID URL:</label>
                <input type="text" name="openid_url" size="60" style="background-image:url('${h.url_for( '/static/images/openid-16x16.gif' )}' ); background-repeat: no-repeat; padding-right: 20px; background-position: 99% 50%;"/>
                <input type="hidden" name="redirect" value="${redirect | h}" size="40"/>
            </div>
            <div class="form-row">
                Or, authenticate with your <select name="openid_provider">
                %for provider in openid_providers:
                    <option value="${provider.id}">${provider.name}</option>
                %endfor
                </select> account.
            </div>
            <div class="form-row">
                <input type="submit" name="login_button" value="Login"/>
            </div>
        </form>
    </div>

</%def>
